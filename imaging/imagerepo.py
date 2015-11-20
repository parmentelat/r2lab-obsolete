from config import the_config
import os.path
import glob

class ImageRepo:
    def __init__(self):
        self.repo = the_config.value('frisbee', 'images_dir')
        self.name = the_config.value('frisbee', 'default_image')
    def default(self):
        return os.path.join(self.repo, self.name)
    def add_extension(self, file):
        for f in (file, file+".ndz"):
            if os.path.exists(f):
                return f
    def locate(self, image):
        return \
          self.add_extension(image) \
           if os.path.isabs(image) \
           else self.add_extension(os.path.join(self.repo, image))

    def display(self):
        # xxx make something nicer
        # show symlinks separately and defaults (ideally by number of links)
        # and then sort real images by size
        print("Contents of image directory {}".format(self.repo))
        for path in glob.glob("{}/*.ndz".format(self.repo)):
            file = path.replace(self.repo+"/", "").replace(self.repo, "")
            print(file)

the_imagerepo = ImageRepo()
