import os
from osgeo import gdal
from PIL import Image
import pyperclip as pc


class TifToUnreal:

    def __init__(self, file_name, map_size, input_file_path, output_path):
        self.file_name = file_name
        self.map_size = int(map_size)
        self.input_file_path = input_file_path
        self.output_path = output_path
        self.geo_tif = gdal.Open(self.input_file_path)

    def convert_map_for_unreal(self):
        limits = self.get_min_max()

        gdal_params = "-ot UInt16 -of PNG -scale " + str(limits[0]) + " " + str(limits[1]) + " 0 65535"
        output_path = self.output_path + self.file_name + ".png"
        full_command = "gdal_translate " + gdal_params + " " + self.input_file_path + " " + output_path
        os.system(full_command)

        self.crop_image()

        z_scale = self.calc_z_scale(limits[0], limits[1])
        # copies z scale to clipboard for ease of use
        pc.copy(z_scale)

        print(f"Map converted for Unreal!\n "
              f"It can be found at {output_path}\n "
              f"Recommended z scale of {z_scale} has been copied to your clipboard!")

    def get_min_max(self):
        # gets min max
        band = self.geo_tif.GetRasterBand(1)
        # Get raster statistics
        stats = band.GetStatistics(True, True)
        # outputs array of max and min
        return stats

    @staticmethod
    def calc_z_scale(min, max):
        # formula from epic
        return (100 * (max - min)) * (1 / 512)

    def crop_image(self):
        im = Image.open(f"{self.output_path}{self.file_name}.png")
        width, height = im.size  # Get dimensions

        new_width, new_height = self.map_size, self.map_size

        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2

        # Crop the center of the image
        im = im.crop((int(left), int(top), int(right), int(bottom)))

        im.save(f"{self.output_path}{self.file_name}_cropped.png")


if __name__ == '__main__':
    # replace is to get rid of the quotes windows LOVES to append when copying path
    class_instance = TifToUnreal(input("Enter file name: "),
                                 input("Enter map size (in pixels): "),
                                 input("Enter input path: ").replace('"', ""),
                                 input("Enter output path: ").replace('"', ""))
    class_instance.convert_map_for_unreal()
