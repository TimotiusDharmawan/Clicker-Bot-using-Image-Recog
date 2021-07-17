# Clicker-Bot-using-Image-Recog
This is a clicker bot used for auto clicking. This project was tested using Mumu Emulator on a game called Arknight.

The steps:
1. Prepare the buttons that need to be clicked by screenshotting the buttons. This will be the template images.
2. Screenshot the whole game screen. This will be used as the base to search the coordinate that matched the tempalte images.
3. Greyscaled and used Canny Edge to preprocess all the images.
4. Iterate to resize the screen image. This was done in case the size of template and screen images did not match.
5. Use <i>CV2.matchTemplate</i> to match the screen and template images. If found, it would return the coordinates of said template image in the screen image.
6. Using the coordinates, randomized the clicking coordinates within the template image's coordinates using Gaussian Distribution.
