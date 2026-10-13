"""Трассировка лучей по элементам модели и атласу: предпросмотр объёмного вида без игры."""
import math
import numpy as np
from PIL import Image

SHADE = {"up": 1.0, "down": 0.5, "north": 0.8, "south": 0.8, "east": 0.6, "west": 0.6}


def _rot(axis, ang):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def render(model, atlas, place, yaw=35, pitch=30, px=9, extent=15.5, bg=(58, 60, 66), center=(8.0, 8.0, 8.0)):
    N = int(extent * 2 * px)
    phi, th = math.radians(yaw), math.radians(pitch)
    P = np.array([math.sin(phi) * math.cos(th), math.sin(th), -math.cos(phi) * math.cos(th)])
    d = -P
    right = np.cross(d, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, d)
    xs = (np.arange(N) - N / 2 + 0.5) / px
    uu, vv = np.meshgrid(xs, -xs)
    center = np.array(center, dtype=float)
    O = center - d * 60 + uu[..., None] * right + vv[..., None] * up
    O = O.reshape(-1, 3)
    at = np.array(atlas)
    H, W = at.shape[0], at.shape[1]
    zbuf = np.full(len(O), 1e9)
    col = np.zeros((len(O), 3))
    col[:] = bg
    trans = []
    for bi, bx in enumerate(model.boxes):
        a = np.array(bx.a, float); b = np.array(bx.b, float)
        Ol, Dl = O, d
        if bx.rot:
            R = _rot(bx.rot["axis"], bx.rot["angle"])
            org = np.array(bx.rot["origin"], float)
            Rinv = R.T
            Ol = (O - org) @ Rinv.T + org if False else (O - org) @ R + org
            Dl = d @ R
        with np.errstate(divide="ignore", invalid="ignore"):
            t1 = (a - Ol) / Dl
            t2 = (b - Ol) / Dl
        tlo = np.minimum(t1, t2); thi = np.maximum(t1, t2)
        tmin = tlo.max(axis=1); tmax = thi.min(axis=1)
        hit = (tmax > tmin) & (tmax > 0)
        axis = tlo.argmax(axis=1)
        Pl = Ol + tmin[:, None] * Dl
        for ax, (fneg, fpos) in enumerate((("west", "east"), ("down", "up"), ("north", "south"))):
            for sign_pos in (False, True):
                fname = fpos if sign_pos else fneg
                if fname not in bx.faces:
                    continue
                dir_ok = (Dl[ax] < 0) if sign_pos else (Dl[ax] > 0)
                m = hit & (axis == ax) & dir_ok
                if not m.any():
                    continue
                p = Pl[m]
                dx, dy, dz = (b - a)
                fr = getattr(bx, "frames", {}).get(fname)
                if fr is not None:
                    Of, Uf, Vf, lu, lv = fr
                    fx = ((p - Of) @ Uf) / lu
                    fy = ((p - Of) @ Vf) / lv
                    rot_f = getattr(bx, "frot", {}).get(fname, 0)
                    if rot_f == 90:
                        fx, fy = fy, 1 - fx
                    elif rot_f == 180:
                        fx, fy = 1 - fx, 1 - fy
                    elif rot_f == 270:
                        fx, fy = 1 - fy, fx
                elif fname == "north":
                    fx, fy = (b[0] - p[:, 0]) / dx, (b[1] - p[:, 1]) / dy
                elif fname == "south":
                    fx, fy = (p[:, 0] - a[0]) / dx, (b[1] - p[:, 1]) / dy
                elif fname == "east":
                    fx, fy = (b[2] - p[:, 2]) / dz, (b[1] - p[:, 1]) / dy
                elif fname == "west":
                    fx, fy = (p[:, 2] - a[2]) / dz, (b[1] - p[:, 1]) / dy
                elif fname == "up":
                    fx, fy = (p[:, 0] - a[0]) / dx, (p[:, 2] - a[2]) / dz
                else:
                    fx, fy = (p[:, 0] - a[0]) / dx, (b[2] - p[:, 2]) / dz
                x0, y0, w, h = place[(bi, fname)]
                sx = np.clip((x0 + fx * w).astype(int), x0, x0 + w - 1)
                sy = np.clip((y0 + fy * h).astype(int), y0, y0 + h - 1)
                texel = at[sy, sx].astype(float)
                alpha = texel[:, 3]
                tt = tmin[m]
                idx = np.where(m)[0]
                shade = SHADE[fname]
                rgb = texel[:, :3] * shade
                opaque = alpha >= 200
                ok = opaque & (tt < zbuf[idx])
                zbuf[idx[ok]] = tt[ok]
                col[idx[ok]] = rgb[ok]
                tr = (alpha >= 40) & (alpha < 200)
                for i_, c_, a_, t_ in zip(idx[tr], rgb[tr], alpha[tr], tt[tr]):
                    trans.append((t_, i_, c_, a_ / 255.0))
    trans.sort(key=lambda r: -r[0])
    for t_, i_, c_, a_ in trans:
        if t_ < zbuf[i_]:
            col[i_] = col[i_] * (1 - a_) + c_ * a_
    img = Image.fromarray(col.reshape(N, N, 3).astype("uint8"), "RGB")
    return img
