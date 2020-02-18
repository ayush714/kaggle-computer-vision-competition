import torch
import pickle
import numpy as np
from torch import nn
from collections import Counter
from yacs.config import CfgNode
from typing import List, Dict, Union
from sklearn.metrics.classification import classification_report
from .loss import MixUpCrossEntropy


class MixUpEvalBlock(nn.Module):

    def __init__(self, loss_cfg: CfgNode):
        super(MixUpEvalBlock, self).__init__()
        self.loss_fn = MixUpCrossEntropy(loss_cfg.OHEM_RATE)

    def forward(self, logits, mixedup_labels_data):
        loss = self.loss_fn(logits, mixedup_labels_data)
        preds = torch.argmax(logits.float(), dim=1)
        labels = mixedup_labels_data[0]
        corrects = (labels == preds)
        acc = torch.sum(corrects) / (len(corrects) + 0.0)
        return loss, acc


class MultiHeadsMixUpEval(nn.Module):

    def __init__(self, solver_cfg: CfgNode):
        super(MultiHeadsMixUpEval, self).__init__()
        loss_cfg = solver_cfg.LOSS

        self.grapheme_eval = MixUpEvalBlock(loss_cfg)
        self.vowel_eval = MixUpEvalBlock(loss_cfg)
        self.consonant_eval = MixUpEvalBlock(loss_cfg)
        self.grapheme_logits_cache = []
        self.vowel_logits_cache = []
        self.consonant_logits_cache = []
        self.labels_cache = []
        self.acc_cache = []
        self.loss_cache = []

    def forward(self, grapheme_logits: torch.Tensor, vowel_logits: torch.Tensor, consonant_logits: torch.Tensor,
                mixup_labels_data: tuple) -> Dict:
        grapheme_labels, shuffled_grapheme_labels, vowel_labels, shuffled_vowel_labels, consonant_labels, shuffled_consonant_labels, lam = mixup_labels_data
        grapheme_mixup_labels = (grapheme_labels, shuffled_grapheme_labels, lam)
        vowel_mixup_labels = (vowel_labels, shuffled_vowel_labels, lam)
        consonant_mixup_labels = (consonant_labels, shuffled_consonant_labels, lam)

        # compute loss
        grapheme_loss, grapheme_acc = self.grapheme_eval(grapheme_logits, grapheme_mixup_labels)
        vowel_loss, vowel_acc = self.vowel_eval(vowel_logits, vowel_mixup_labels)
        consonant_loss, consonant_acc = self.consonant_eval(consonant_logits, consonant_mixup_labels)
        loss = grapheme_loss + vowel_loss + consonant_loss
        acc = (grapheme_acc + vowel_acc + consonant_acc) / 3
        eval_result = {
            'grapheme_loss': grapheme_loss,
            'grapheme_acc': grapheme_acc,
            'vowel_loss': vowel_loss,
            'vowel_acc': vowel_acc,
            'consonant_loss': consonant_loss,
            'consonant_acc': consonant_acc,
            'loss': loss,
            'acc': acc
        }
        labels = torch.stack([grapheme_labels, vowel_labels, consonant_labels]).T
        # dump data in cache
        self.grapheme_logits_cache.append(grapheme_logits.detach().cpu().numpy())
        self.vowel_logits_cache.append(vowel_logits.detach().cpu().numpy())
        self.consonant_logits_cache.append(consonant_logits.detach().cpu().numpy())
        self.labels_cache.append(labels.detach().cpu().numpy())
        self.loss_cache.append(loss.detach().item())
        self.acc_cache.append(acc.detach().item())
        return eval_result

    def clear_cache(self):
        self.grapheme_logits_cache = []
        self.vowel_logits_cache = []
        self.consonant_logits_cache = []
        self.labels_cache = []
        self.loss_cache = []
        self.acc_cache = []

    def evalulate_on_cache(self):
        grapheme_logits_all = np.vstack(self.grapheme_logits_cache)
        vowel_logits_all = np.vstack(self.vowel_logits_cache)
        consonant_logits_all = np.vstack(self.consonant_logits_cache)
        labels_all = np.vstack(self.labels_cache)

        grapheme_preds = np.argmax(grapheme_logits_all, axis=1)
        vowels_preds = np.argmax(vowel_logits_all, axis=1)
        consonant_preds = np.argmax(consonant_logits_all, axis=1)

        grapheme_clf_result = classification_report(labels_all[:, 0], grapheme_preds, output_dict=True)
        vowels_clf_result = classification_report(labels_all[:, 1], vowels_preds, output_dict=True)
        consonant_clf_result = classification_report(labels_all[:, 2], consonant_preds, output_dict=True)
        kaggle_score = (grapheme_clf_result['macro avg']['recall'] * 2 + vowels_clf_result['macro avg']['recall'] +
                        consonant_clf_result['macro avg']['recall']) / 4

        preds_labels = []
        for idx, grapheme_pred in enumerate(grapheme_preds):
            vowel_pred = vowels_preds[idx]
            consonant_pred = consonant_preds[idx]
            labels = labels_all[idx]
            entry = {
                'grapheme_pred': grapheme_pred,
                'vowel_pred': vowel_pred,
                'consonant_pred': consonant_pred,
                'grapheme_label': labels[0],
                'vowel_label': labels[1],
                'consonant_label': labels[2]
            }
            preds_labels.append(entry)

        grapheme_clf_result = clf_result_helper(grapheme_clf_result, preds_labels, 'grapheme_pred', 'grapheme_label')
        vowels_clf_result = clf_result_helper(vowels_clf_result, preds_labels, 'vowel_pred', 'vowel_label')
        consonant_clf_result = clf_result_helper(consonant_clf_result, preds_labels, 'consonant_pred',
                                                 'consonant_label')

        acc = np.mean(self.acc_cache)
        loss = np.mean(self.loss_cache)
        result = {
            'grapheme_clf_result': grapheme_clf_result,
            'vowel_clf_result': vowels_clf_result,
            'consonant_clf_result': consonant_clf_result,
            'kaggle_score': kaggle_score,
            'preds_labels': preds_labels,
            'acc': acc,
            'loss': loss
        }
        return result


def clf_result_helper(clf_result: Dict, preds_labels: List, pred_key: str, label_key: str):
    """
    a helper function get per class result the highest error class, and highest error class occurences
    :param clf_result:  classfier result dict from classificaiton_report
    :param preds_labels: list of preds and labels
    :param pred_key:  one of [grapheme_pred, vowel_pred, consonant_pred]
    :param label_key: one of [grapheme_label, vowel_label, consonant_label]
    :return: list view of clf result with some added info
    """
    for k in clf_result.keys():
        if k not in ['accuracy', 'macro avg', 'weighted avg']:
            cls = int(k)
            preds_counts = Counter([x[pred_key] for x in preds_labels if x[label_key] == cls])
            preds_counts = [[k, preds_counts[k]] for k in preds_counts]
            incorrect_preds_counts = [x for x in preds_counts if x[0] != cls]
            if len(incorrect_preds_counts) > 0:
                highest_error_cls, highest_error_cls_num = sorted(incorrect_preds_counts, key=lambda x: x[1])[-1]
            else:
                highest_error_cls, highest_error_cls_num = -1, 0

            clf_result[k]['class'] = cls
            clf_result[k]['error_cls'] = highest_error_cls
            if clf_result[k]['support'] > 0:
                clf_result[k]['error_cls_rate'] = highest_error_cls_num / clf_result[k]['support']
            else:
                clf_result[k]['error_cls_rate'] = 0
    clf_result = [clf_result[k] for k in clf_result if k not in ['accuracy', 'macro avg', 'weighted avg']]
    return clf_result
