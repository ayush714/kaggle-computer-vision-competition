from yacs.config import CfgNode as ConfigurationNode

# YACS overwrite these settings using YAML

__C = ConfigurationNode()

# importing default as a global singleton
cfg = __C
__C.DESCRIPTION = 'Default config'
__C.DATASET = ConfigurationNode()
__C.DATASET.NAME = 'bengali_kaggle'
__C.DATASET.DEFAULT_SIZE = (137, 236)
__C.DATASET.RESIZE_SHAPE = (128, 128)
__C.DATASET.WHITE_BACKGROUND = True
__C.DATASET.CONCENTRATE_CROP = True
__C.DATASET.PAD_TO_SQUARE = False
__C.DATASET.GRAPHEME_SIZE = 168
__C.DATASET.VOWEL_SIZE = 11
__C.DATASET.CONSONANT_SIZE = 7
__C.DATASET.TRAIN_DATA_PATH = 'C:/Users/mingy/Documents/ml_data/bengali/train_data.p'
__C.DATASET.VAL_DATA_PATH = 'C:/Users/mingy/Documents/ml_data/bengali/val_data.p'

# augmix related parameters
__C.DATASET.DO_AUGMIX = False

__C.DATASET.AUGMENTATION = ConfigurationNode()
__C.DATASET.AUGMENTATION.BLURRING_PROB = 0.25
__C.DATASET.AUGMENTATION.GAUSS_NOISE_PROB = 0.25
__C.DATASET.AUGMENTATION.BRIGHTNESS_CONTRAST_PROB = 1
__C.DATASET.AUGMENTATION.GRID_DISTORTION_PROB = 1
__C.DATASET.AUGMENTATION.ROTATION_PROB = 1
__C.DATASET.AUGMENTATION.ROTATION_DEGREE = 20
__C.DATASET.AUGMENTATION.GRID_MASK_PROB = 0.0
__C.DATASET.BATCH_SIZE = 32
__C.DATASET.CPU_NUM = 4
__C.DATASET.TO_RGB = True
__C.DATASET.NORMALIZE_MEAN = [0.485, 0.456, 0.406]
__C.DATASET.NORMALIZE_STD = [0.229, 0.224, 0.225]
__C.DATASET.FOCUS_CLASS = []

__C.MODEL = ConfigurationNode()
__C.MODEL.META_ARCHITECTURE = 'baseline'
__C.MODEL.NORMALIZATION_FN = 'BN'

__C.MODEL.BACKBONE = ConfigurationNode()
__C.MODEL.BACKBONE.NAME = 'mobilenet_v2'
__C.MODEL.BACKBONE.RGB = True
__C.MODEL.BACKBONE.PRETRAINED_PATH = r'C:\Git\bengali.ai\models\mobilenet_v2-b0353104.pth'

__C.MODEL.HEAD = ConfigurationNode()
__C.MODEL.HEAD.NAME = 'simple_head'
__C.MODEL.HEAD.ACTIVATION = 'leaky_relu'
__C.MODEL.HEAD.OUTPUT_DIMS = [168, 11, 7]
__C.MODEL.HEAD.INPUT_DIM = 1280  # mobilenet V2
__C.MODEL.HEAD.HIDDEN_DIMS = [512, 256]
__C.MODEL.HEAD.BN = True
__C.MODEL.HEAD.DROPOUT = -1

__C.MODEL.SOLVER = ConfigurationNode()
__C.MODEL.SOLVER.OPTIMIZER = ConfigurationNode()
__C.MODEL.SOLVER.OPTIMIZER.BASE_LR = 0.001
__C.MODEL.SOLVER.OPTIMIZER.NAME = 'adam'

# sgd config
__C.MODEL.SOLVER.OPTIMIZER.SGD = ConfigurationNode()
__C.MODEL.SOLVER.OPTIMIZER.SGD.MOMENTUM = 0.9
__C.MODEL.SOLVER.OPTIMIZER.SGD.NESTEROV = False

__C.MODEL.SOLVER.SCHEDULER = ConfigurationNode()
__C.MODEL.SOLVER.SCHEDULER.NAME = 'unchange'
__C.MODEL.SOLVER.SCHEDULER.LR_REDUCE_GAMMA = 0.1
__C.MODEL.SOLVER.SCHEDULER.MULTI_STEPS_LR_MILESTONES = []

__C.MODEL.SOLVER.TOTAL_EPOCHS = 40
__C.MODEL.SOLVER.AMP = False
__C.MODEL.SOLVER.MIXUP_AUGMENT = False
__C.MODEL.SOLVER.MIXUP = ConfigurationNode()
__C.MODEL.SOLVER.MIXUP.ALPHA = 1.0
__C.MODEL.SOLVER.MIXUP.CUTMIX_PROB = 0.0

__C.MODEL.SOLVER.LOSS = ConfigurationNode()

__C.MODEL.SOLVER.LOSS.OHEM_RATE = 1.0
__C.MODEL.SOLVER.LOSS.NAME = 'xentropy'
__C.MODEL.SOLVER.LOSS.LABELS_WEIGHTS_PATH = 'C:/Users/mingy/Documents/ml_data/bengali/labels_weights.p'

# focal loss related
__C.MODEL.SOLVER.LOSS.FOCAL_LOSS = ConfigurationNode()
__C.MODEL.SOLVER.LOSS.FOCAL_LOSS.GAMMA = 1
__C.MODEL.SOLVER.LOSS.FOCAL_LOSS.ALPHA = -1

__C.OUTPUT_PATH = ''
__C.RESUME_PATH = ''


def get_cfg_defaults():
    """
    Get a yacs CfgNode object with default values for my_project.
    """
    # Return a clone so that the defaults will not be altered
    # This is for the "local variable" use pattern recommended by the YACS repo.
    # It will be subsequently overwritten with local YAML.
    return __C.clone()
