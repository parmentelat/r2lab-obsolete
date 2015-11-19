from config import the_config
import os.path
import glob

class ImageRepo:
    def __init__(self):
        self.repo = the_config.value('frisbee', 'images_dir')
        self.name = the_config.value('frisbee', 'default_image')
    def default(self):
        return os.path.join(self.repo, self.name)
    def locate(self, image):
        if os.path.isabs(image):
            return os.path.exists(image) and image
        else:
            image = os.path.join(self.repo, image)
            return os.path.exists(image) and image
    def display(self):
        # xxx make something nicer
        # show symlinks and defaults etc...
        print("Contents of image directory {}".format(self.repo))
        for path in glob.glob("{}/*".format(self.repo)):
            file = path.replace(self.repo, "")
            print(file)
