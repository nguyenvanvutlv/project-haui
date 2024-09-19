from models.noisereduce.spectralgate.nonstationary import SpectralGateNonStationary
from models.noisereduce.spectralgate.stationary import SpectralGateStationary
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
if TORCH_AVAILABLE:
    from models.noisereduce.spectralgate.streamed_torch_gate import StreamedTorchGate
