import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class CausalConv1d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation=1, **kwargs):
        super(CausalConv1d, self).__init__()
        self.padding = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(
            in_channels, 
            out_channels,
            kernel_size,
            padding=self.padding,
            dilation=dilation,
            **kwargs
        )
    
    def forward(self, x):
        result = self.conv(x)
        if self.padding != 0:
            return result[:, :, :-self.padding]
        return result

class TCNResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation, dropout=0.2):
        super(TCNResidualBlock, self).__init__()
        self.conv1 = CausalConv1d(
            in_channels, 
            out_channels, 
            kernel_size, 
            dilation=dilation
        )
        self.norm1 = nn.BatchNorm1d(out_channels)
        self.dropout1 = nn.Dropout(dropout)
        self.conv2 = CausalConv1d(
            out_channels, 
            out_channels, 
            kernel_size, 
            dilation=dilation
        )
        self.norm2 = nn.BatchNorm1d(out_channels)
        self.dropout2 = nn.Dropout(dropout)
        if in_channels != out_channels:
            self.residual = nn.Conv1d(in_channels, out_channels, 1)
        else:
            self.residual = nn.Identity()
    
    def forward(self, x):
        out = self.conv1(x)
        out = self.norm1(out)
        out = F.relu(out)
        out = self.dropout1(out)
        out = self.conv2(out)
        out = self.norm2(out)
        out = F.relu(out)
        out = self.dropout2(out)
        res = self.residual(x)
        return F.relu(out + res)

class TCN(nn.Module):
    def __init__(self, input_size, output_size, num_channels, kernel_size, dropout):
        super(TCN, self).__init__()
        self.tcn_block = TCNResidualBlock(
            in_channels=input_size,
            out_channels=num_channels,
            kernel_size=kernel_size,
            dilation=2,
            dropout=dropout
        )
        self.linear = nn.Linear(num_channels, output_size)
    
    def forward(self, x):
        x = x.transpose(1, 2)
        y = self.tcn_block(x)
        y = y[:, :, -1]
        return self.linear(y)

if __name__ == "__main__":
    batch_size = 1
    sequence_length = 10
    input_size = 3
    model = TCN(
        input_size=input_size,
        output_size=1,
        num_channels=32,
        kernel_size=3,
        dropout=0.2
    )
    x = torch.randn(batch_size, sequence_length, input_size)
    output = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print("Model architecture:")
    print(model)
