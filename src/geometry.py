import numpy as np
from scipy.spatial.transform import Rotation


class Vector:
    __slots__ = ('_np_arr',)
    _size = 1
    _letters = ('x', 'y', 'z', 'w')

    def __init__(self, arr=None, dtype=None):
        if arr is None:
            arr = np.ndarray(self._size, dtype=dtype)
        self._np_arr = arr

    def __getitem__(self, key):
        return self._np_arr[key]

    def __setitem__(self, key, value):
        self._np_arr[key] = value

    def __mul__(self, other):
        cls = type(self)
        if cls is not type(other):
            raise TypeError("Vector multiplication type mismatch: {} vs {}".format(cls, type(other)))
        return cls(self._np_arr * other._np_arr)

    def __repr__(self):
        return type(self).__name__ + "(" + ",".join(
            "{}={}".format(
                self._letters[i],
                getattr(self, self._letters[i])
            ) for i in range(self._size)
        ) + ")"

    __str__= __repr__

    def normalize(self):
        return type(self)(self._np_arr / np.linalg.norm(self._np_arr))

    def cross(self, other):
        return type(self)(np.cross(self._np_arr, other._np_arr))

    def dot(self, other):
        return type(self)(np.dot(self._np_arr, other._np_arr))

    @classmethod
    def origin(cls):
        return cls(np.array([0] * cls._size))


class Vector2(Vector):
    _size = 2

    @property
    def x(self):
        return self._np_arr[0]

    @x.setter
    def x(self, value: float):
        self._np_arr[0] = value

    @property
    def y(self):
        return self._np_arr[1]

    @y.setter
    def y(self, value: float):
        self._np_arr[1] = value

    @classmethod
    def up(cls):
        return cls(np.array([0, 1]))

    @classmethod
    def down(cls):
        return cls(np.array([0, -1]))

    @classmethod
    def left(cls):
        return cls(np.array([-1, 0]))

    @classmethod
    def right(cls):
        return cls(np.array([1, 0]))


class Vector3(Vector):
    _size = 3

    @property
    def x(self):
        return self._np_arr[0]

    @x.setter
    def x(self, value: float):
        self._np_arr[0] = value

    @property
    def y(self):
        return self._np_arr[1]

    @y.setter
    def y(self, value: float):
        self._np_arr[1] = value

    @property
    def z(self):
        return self._np_arr[2]

    @z.setter
    def z(self, value: float):
        self._np_arr[2] = value

    @classmethod
    def up(cls):
        return cls(np.array([0, 1, 0]))

    @classmethod
    def down(cls):
        return cls(np.array([0, -1, 0]))

    @classmethod
    def left(cls):
        return cls(np.array([-1, 0, 0]))

    @classmethod
    def right(cls):
        return cls(np.array([1, 0, 0]))

    @classmethod
    def forward(cls):
        return cls(np.array([0, 0, 1]))

    @classmethod
    def backward(cls):
        return cls(np.array([0, 0, -1]))

    def rotate(self, rotation: Rotation, origin = None):
        if origin is None:
            origin = Vector3.origin()
        return Vector3(np.add(rotation.apply(np.subtract(self._np_arr, origin._np_arr)), origin._np_arr))

    def rotationTo(self, other) -> Rotation:
        rotation, _ = Rotation.align_vectors([other._np_arr], [self._np_arr])
        return rotation


class Vector4(Vector):
    _size = 4

    @property
    def x(self):
        return self._np_arr[0]

    @x.setter
    def x(self, value: float):
        self._np_arr[0] = value

    @property
    def y(self):
        return self._np_arr[1]

    @y.setter
    def y(self, value: float):
        self._np_arr[1] = value

    @property
    def z(self):
        return self._np_arr[2]

    @z.setter
    def z(self, value: float):
        self._np_arr[2] = value

    @property
    def w(self):
        return self._np_arr[3]

    @w.setter
    def w(self, value: float):
        self._np_arr[3] = value


class TransformMatrix:
    __slots__ = ('_np_arr',)

    def __init__(self, arr = None):
        if arr is None:
            arr = np.ndarray((4,4))
        self._np_arr = arr

    def __getitem__(self, key):
        return self._np_arr[key]

    def __setitem__(self, key, value):
        self._np_arr[key] = value

    def apply(self, point: Vector3):
        point4 = np.ndarray(4)
        point4[:3] = point._np_arr
        point4[3] = 1
        result = self._np_arr @ point4
        result.resize(3)
        return Vector3(result)

    @classmethod
    def identity(cls):
        return cls(np.identity(4))

    def inverse(self):
        return type(self)(np.linalg.inv(self._np_arr))

    def __repr__(self) -> str:
        return repr(self._np_arr)

    def __str__(self) -> str:
        return str(self._np_arr)

    def transpose(self):
        return type(self)(np.transpose(self._np_arr))