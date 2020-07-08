# Standard library imports
import os

# Third party imports
import netCDF4

# Repo paths
SRC_PATH = "data/so2_original/"
DST_PATH = "data/so2/"


def copy_selected_variables(file_a, file_b, vars_to_copy):

    with netCDF4.Dataset(file_a) as src, netCDF4.Dataset(file_b, "w") as dst:

        # Copy attributes
        for name in src.ncattrs():
            dst.setncattr(name, src.getncattr(name))

        # Copy dimensions
        for name, dimension in src.dimensions.items():
            dst.createDimension(name, (len(dimension) if not dimension.isunlimited() else None))

        # Copy all file data for selected variables
        for name, variable in src.variables.items():
            if name in vars_to_copy:
                x = dst.createVariable(
                    varname=name,
                    datatype=variable.datatype,
                    dimensions=variable.dimensions
                )

                # Copy variable attributes all at once via dictionary
                dst[name].setncatts(src[name].__dict__)

                # Copy variable values
                dst[name][:] = src[name][:]


if __name__ == '__main__':

    variables = ['longitude', 'latitude', 't', 'surface', 'temp', 'precip', 'field569', 'field569_1']

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
                    vars_to_copy=variables
                )
