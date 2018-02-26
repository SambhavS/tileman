import random

def gen_mat(i0, i1, j0, j1, mat, func):
    new_mat = []
    for a in range(i0, i1):
        row = []
        for b in range(j0, j1):
            row.append(func(a, b, i0, i1, j0, j1, mat))
        new_mat.append(row)
    return new_mat

def submat(i0, i1, j0, j1, mat):
    return [mat[i][j0:j1] for i in range(i0,i1)]

def fill2Dmat(a, b, func):
    return gen_mat(0, a, 0, b, None, lambda a, b, i0, i1, j0, j1, mat: func(a, b))

def empty_mat(a, b):
    return fill2Dmat(a, b, lambda x, y: 0)

def rand_mat(a, b, seed):
    rand_obj = random.Random(seed)
    return fill2Dmat(a, b, lambda x, y : 4 + round(rand_obj.random()*0.7))

def create_basemat(k, tiles_wide, tiles_high):
    row = [k] * tiles_wide
    return [row[::] for i in range(tiles_high)]

def out_bounds(mat, i, j):
    return i < 0 or j < 0 or i >= len(mat) or j >= len(mat[0])