import bottler
from example import view_models
import os
import example

##### Bottler Settings #####
bottler_settings = {
    "project_routes": example.v1_routes,
    "view_models": view_models,

    "base_path": os.getcwd() + "../",
    "wiki_path": os.getcwd() + "/",

    #Debug set to 'True' will print statements to quickly find
    #cause of handler(s) which do not conform to the bottler's expectations
    "debug": False,
}

if __name__ == "__main__":
    bottler.main(bottler_settings)