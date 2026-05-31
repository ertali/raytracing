# imports
import math
import random


# 3d vector class
class vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    # series of dunder operations for vec3

    # addition
    def __add__(self, other):
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    # subtraction
    def __sub__(self, other):
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    # negation
    def __neg__(self):
        return vec3(-self.x, -self.y, -self.z)

    # multiplication (scalar or element wise)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return vec3(self.x * other, self.y * other, self.z * other)
        elif isinstance(other, vec3):
            return vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    # handles scalar * vector

    def __rmul__(self, other):
        return self * other

    # division by scalar

    def __truediv__(self, other):
        return vec3(self.x / other, self.y / other, self.z / other)

    # cross product (overwriting the & method)
    def __and__(self, other):
        return vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    # dot product (overwriting the matrix multiplication method)
    def __matmul__(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    # length method (square roots the square length)
    @property
    def len(self):
        return math.sqrt(self.square_len)

    # square length method
    @property
    def square_len(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    # normalized vector
    @property
    def unit(self):
        l = self.len
        return vec3(self.x / l, self.y / l, self.z / l)

    # string output
    def __str__(self):
        return f"{self.x} {self.y} {self.z}"


# ray class
class ray:
    def __init__(self, A, b):
        self.A = A
        self.b = b

    def at(self, t):
        return self.A + t * self.b


# interval class
class interval:
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def size(self):
        return self.maximum - self.minimum

    def contains(self, x):
        return self.minimum <= x and x <= self.maximum

    def surrounds(self, x):
        return self.minimum < x and x < self.maximum

    def clamp(self, x):
        if x < self.minimum:
            return self.minimum
        elif x > self.maximum:
            return self.maximum
        return x

    @classmethod
    def empty(cls):
        return cls(math.inf, -math.inf)

    @classmethod
    def universe(cls):
        return cls(-math.inf, math.inf)


# camera class
class camera:
    def __init__(self, aspect_ratio, image_width, samples_per_pixel):
        self.aspect_ratio = aspect_ratio
        self.image_width = image_width
        self.samples_per_pixel = samples_per_pixel

    def render(self, world, filename):
        self.initialize()

        for j in range(self.image_height):
            if (self.image_height - j) % 50 == 0:
                print(
                    f"Scanlines remaining: {self.image_height - j} out of {self.image_height}"
                )

            for i in range(self.image_width):
                pixel_color = vec3(0, 0, 0)
                for k in range(0, self.samples_per_pixel):
                    r = self.get_ray(i, j)
                    pixel_color += self.ray_color(r, world)
                self.image_list.append(
                    f"{write_color(self.pixel_samples_scale * pixel_color)}\n"
                )

        write_ppm(filename, self.image_width, self.image_height, self.image_list)

    def initialize(self):
        self.image_height = int(self.image_width / self.aspect_ratio)
        self.image_list = []

        viewport_height = 2
        viewport_width = viewport_height * (self.image_width / self.image_height)
        focal_length = 1

        self.pixel_samples_scale = 1 / self.samples_per_pixel

        self.camera_center = vec3(0, 0, 0)

        # Calculating vectors across the horizontal and down the vertical viewport edges
        viewport_u = vec3(viewport_width, 0, 0)
        viewport_v = vec3(0, -viewport_height, 0)

        # Calculating the horizontal and vertical delta vectors from pixel to pixel
        self.pixel_delta_u = viewport_u / self.image_width
        self.pixel_delta_v = viewport_v / self.image_height

        # Calculate the location of the upper left pixel
        viewport_upper_left = (
            self.camera_center
            - vec3(0, 0, focal_length)
            - viewport_u / 2
            - viewport_v / 2
        )
        self.pixel00_loc = viewport_upper_left + 0.5 * (
            self.pixel_delta_u + self.pixel_delta_v
        )

    def ray_color(self, input_ray, world):
        temp_rec = world.hit(input_ray, interval(0, math.inf))
        if temp_rec:
            return 0.5 * (temp_rec.normal + vec3(1, 1, 1))

        unit_direction = input_ray.b.unit
        a = 0.5 * (unit_direction.y + 1)
        return (1.0 - a) * vec3(1, 1, 1) + a * vec3(0.5, 0.7, 1.0)

    def get_ray(self, i, j):
        offset = self.sample_square()

        pixel_sample = (
            self.pixel00_loc
            + ((i + offset.x) * self.pixel_delta_u)
            + ((j + offset.y) * self.pixel_delta_v)
        )

        ray_origin = self.camera_center
        ray_direction = pixel_sample - ray_origin

        return ray(ray_origin, ray_direction)

    def sample_square(self):
        return vec3(random.random() - 0.5, random.random() - 0.5, 0)


# class that handles how hitting works
class hit_record:
    def __init__(self, p=None, normal=None, t=None, front_face=None):
        self.p = p
        self.normal = normal
        self.t = t
        self.front_face = front_face

    def set_face_normal(self, r, outward_normal):
        self.front_face = (r.b @ outward_normal) < 0
        self.normal = outward_normal if self.front_face else -outward_normal


# defines a generic hittable 'object' class
class hittable:
    def hit(self, input_ray, ray_t):
        raise NotImplementedError("Subclasses must implement this method!")


# subclass of hittable for storing a list of hittables
class hittable_list(hittable):
    def __init__(self, objects):
        if objects is None:
            self.objects = []
        else:
            self.objects = objects

    def add(self, hittable_object):
        self.objects.append(hittable_object)

    def hit(self, input_ray, ray_t):
        closest_rec = None
        closest_t = ray_t.maximum
        for i in self.objects:
            temp_rec = i.hit(input_ray, interval(ray_t.minimum, closest_t))
            if (temp_rec is not False) and (temp_rec.t < closest_t):
                closest_rec = temp_rec
                closest_t = temp_rec.t
        return closest_rec


# subclass of hittable for spheres
class sphere(hittable):
    def __init__(self, center, radius):
        self.center = center
        self.radius = max(0, radius)

    def hit(self, input_ray, ray_t):
        oc = self.center - input_ray.A
        a = input_ray.b.square_len
        h = input_ray.b @ oc
        c = oc.square_len - self.radius * self.radius
        discriminant = h * h - a * c

        if discriminant < 0:
            return False

        sqrtd = math.sqrt(discriminant)

        root = (h - sqrtd) / a
        if ray_t.surrounds(root) is False:
            root = (h + sqrtd) / a
            if ray_t.surrounds(root) is False:
                return False

        temp_rec = hit_record()

        temp_rec.t = root
        temp_rec.p = input_ray.at(temp_rec.t)
        outward_normal = (temp_rec.p - self.center) / self.radius
        temp_rec.set_face_normal(input_ray, outward_normal)

        return temp_rec


"""DEPRECATED
# utility function to return color for a given scene ray
def ray_color(input_ray, world):
    temp_rec = world.hit(input_ray, interval(0, math.inf))
    if temp_rec:
        return 0.5 * (temp_rec.normal + vec3(1, 1, 1))

    unit_direction = input_ray.b.unit
    a = 0.5 * (unit_direction.y + 1)
    return (1.0 - a) * vec3(1, 1, 1) + a * vec3(0.5, 0.7, 1.0)
"""

"""DEPRECATED
# utility function to see if we hit the sphere
def hit_sphere(center, radius, r):
    oc = center - r.A
    DEPRECATED
    a = r.b @ r.b
    b = -2 * (r.b @ oc)
    c = (oc @ oc) - radius * radius
    discriminant = b * b - 4 * a * c
    a = r.b.square_len
    h = r.b @ oc
    c = oc.square_len - radius * radius
    discriminant = h * h - a * c

    if discriminant < 0:
        return -1
    else:
        return h - math.sqrt(discriminant) / a
"""


# utility function for writing colors during the render
def write_color(colors):
    r = colors.x
    g = colors.y
    b = colors.z

    intensity = interval(0, 1)
    rbyte = int(256 * intensity.clamp(r))
    gbyte = int(256 * intensity.clamp(g))
    bbyte = int(256 * intensity.clamp(b))

    return str(vec3(rbyte, gbyte, bbyte))


# utility function to write ppm outputs
# filename must be a string
# color range is 256 by default
# values is the list produced after the line by line scan
def write_ppm(filename, width, height, values):
    with open(f"{filename}.ppm", "w") as f:
        f.write("P3\n")
        f.write(f"{width} {height}\n")
        f.write("256\n")
        f.writelines(values)
        print(f"Write of {filename} complete!")
