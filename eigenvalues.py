# From scratch for a simple 2x2 matrix

def calculate_eigenvalues(matrix: list[list[float|int]])->list[float]:
    eigenvalues = []
    a, b = matrix[0]
    c, d = matrix[1]

    trace = a + d
    det = a * d - b * c

    delta = (-trace) ** 2 - 4 * det

    if delta >= 0:
        sqrt_delta = delta ** 0.5
    else:
        sqrt_delta = ((-delta)**0.5) * 1j
    
    eigenvalues.append((trace + sqrt_delta) / 2)
    eigenvalues.append((trace - sqrt_delta) / 2)

    return eigenvalues

# With Pytorch
import torch
from torch import linalg
import math

A = torch.tensor([[math.cos(45), math.sin(45), 0], [-math.sin(45), math.cos(45), 0], [0, 0, 1]])
l, e = linalg.eig(A)
print("Eigenvalues are \n{}\n".format(l))
print("Eigenvectors are \n{}\n".format(e))


if __name__ == "__main__":
    matrix = [[2, 1],
              [1, 2]]
    print(calculate_eigenvalues(matrix=matrix))