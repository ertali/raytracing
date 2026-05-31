from PIL import Image

from utils import (
    camera,
    hittable_list,
    sphere,
    vec3,
)

image_height = 256
image_width = 256
image_list = []

world = hittable_list([])
world.add(sphere(vec3(0, 0, -1), 0.5))
world.add(sphere(vec3(0, -100.5, -1), 100))

cam = camera(16 / 9, 400, 100)

cam.render(world, "example_output")
with Image.open("example_output.ppm") as img:
    img.save("example_output.png", "PNG")


"""
# Generate PPM image
for i in range(image_height):
    if (image_height - i) % 50 == 0:
        print(f"Scanlines remaining: {image_height - i} out of {image_height}")
    for j in range(image_width):
        r = (j) / (image_width - 1)
        g = (i) / (image_width - 1)
        b = 0

        ir = int(256 * r)
        ig = int(256 * g)
        ib = int(256 * b)

        image_list.append(f"{ir} {ig} {ib}\n")
write_ppm("first", image_width, image_height, image_list)

image_list = []

# updated the first image's code to use the new vec3
for i in range(image_height):
    if (image_height - i) % 50 == 0:
        print(f"Scanlines remaining: {image_height - i} out of {image_height}")
    for j in range(image_width):
        pixels = vec3((j) / (image_width - 1), (i) / (image_width - 1), 0)

        image_list.append(f"{write_color(pixels)}\n")
write_ppm("second", image_width, image_height, image_list)
"""

""" DEPRECATED
# first ray traced image

# Image details
aspect_ratio = 16 / 9
image_width = 400
image_height = int(image_width / aspect_ratio)
image_list = []

# Camera details
viewport_height = 2
viewport_width = viewport_height * (image_width / image_height)
focal_length = 1
camera_center = vec3(0, 0, 0)

# Calculating vectors across the horizontal and down the vertical viewport edges
viewport_u = vec3(viewport_width, 0, 0)
viewport_v = vec3(0, -viewport_height, 0)

# Calculating the horizontal and vertical delta vectors from pixel to pixel
pixel_delta_u = viewport_u / image_width
pixel_delta_v = viewport_v / image_height


# Calculate the location of the upper left pixel
viewport_upper_left = (
    camera_center - vec3(0, 0, focal_length) - viewport_u / 2 - viewport_v / 2
)
pixel00_loc = viewport_upper_left + 0.5 * (pixel_delta_u + pixel_delta_v)

# Render PPM
for j in range(image_height):
    if (image_height - j) % 50 == 0:
        print(f"Scanlines remaining: {image_height - j} out of {image_height}")
    for i in range(image_width):
        pixel_center = pixel00_loc + (i * pixel_delta_u) + (j * pixel_delta_v)
        ray_direction = pixel_center - camera_center
        r = ray(camera_center, ray_direction)

        pixel_color = ray_color(r)
        image_list.append(f"{write_color(pixel_color)}\n")
write_ppm("third", image_width, image_height, image_list)
"""
