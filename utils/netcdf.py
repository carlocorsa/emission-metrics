# Standard library imports
import os

# Third party imports
import netCDF4

# Repo paths
SRC_PATH = "data/so2_original/"
DST_PATH = "data/so2/"


def copy_selected_variables(file_a, file_b, variables):

    with netCDF4.Dataset(file_a) as src, netCDF4.Dataset(file_b, "w") as dst:

        # Copy attributes
        for name in src.ncattrs():
            dst.setncattr(name, src.getncattr(name))

        # Copy dimensions
        for name, dimension in src.dimensions.items():
            if dimension.isunlimited():
                dst.createDimension(name, None)
            else:
                dst.createDimension(name, len(dimension))

        # Copy all file data for selected variables
        for name, variable in src.variables.items():
            if name in variables:
                x = dst.createVariable(name, variable.datatype, variable.dimensions)
                dst.variables[name][:] = src.variables[name][:]


if __name__ == '__main__':

    vars_to_copy = ['longitude', 'latitude', 't', 'surface', 'temp', 'precip', 'field569', 'field569_1']

    for folder in os.listdir(SRC_PATH):

        if "No_SO2" in folder:
            src_folder_path = os.path.join(SRC_PATH, folder)
            dst_folder_path = os.path.join(DST_PATH, folder)

            if not os.path.exists(dst_folder_path):
                os.mkdir(dst_folder_path)

            for file in os.listdir(src_folder_path):

                copy_selected_variables(
                    file_a=os.path.join(src_folder_path, file),
                    file_b=os.path.join(dst_folder_path, file),
                    variables=vars_to_copy
                )
