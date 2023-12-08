import cv2
from collections import Counter
import numpy as np
from sklearn.cluster import KMeans
from kneed import KneeLocator
from sklearn.utils import shuffle
from shapely.geometry import Polygon, Point
import svgwrite
import json
import random

# Change me to an integer for consistent results between runs, or set to None to allow randomness in K-means
random_state = None


class PbnGen:
    def __init__(
        self,
        bgr_image,
        num_colors=None,
        min_num_colors=10,
        pruningThreshold=6.25e-5,
        max_resolution=200000,
        min_percent_area=0.001,
    ):
        # bgr_image = cv2.imread(f_name)
        # change to RGB
        rgbImage = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

        # Retain an original image copy for easy testing
        self.originalImage = rgbImage
        self.originalImg1d = self.get1DImg(self.originalImage)

        # Set the actual working image to a copy of the original
        self.setImage(self.originalImage.copy())

        # The minimum percentage of the image's area a color cluster can be before getting absorbed by surrounding colors
        self.pruningThreshold = pruningThreshold

        self.max_resolution = max_resolution

        self.min_percent_area = min_percent_area

        # This will contain a dict of colors and binary masks of the pruned clusters
        self.prunableClusters = None

        self.num_colors = num_colors if num_colors else self.get_num_clusters()
        # make sure number of colors is at least minimum number
        self.num_colors = (
            self.num_colors + min_num_colors
            if self.num_colors < min_num_colors
            else self.num_colors
        )
        print(f"Quantized to {self.num_colors} colors")

    def cluster_colors(self) -> "tuple[np.ndarray, np.ndarray, np.ndarray]":
        """
        Performs K means clustering on the image to quantize it to a fixed number of colors.

        Returns:
            (palette, labels, q_img)

            palette: A (N, 3) numpy array representing the quantized colors in a float32 format.
            labels: A (H*W,) numpy array which holds the assigned labels for each pixel in the image.
            q_img: A (H, W, 3) quantized image which holds the original image quantized to the specified number of colors.
        """

        model = KMeans(
            n_clusters=self.num_colors, n_init="auto", random_state=random_state
        )
        model.fit(self.img1d)

        # get primary colors as floats from 0 to 1
        self.palette = model.cluster_centers_ / 255
        self.labels = model.labels_
        # get quantized image
        q_img = self.palette[self.labels].reshape(self.image.shape)
        return self.palette, self.labels, q_img

    def cluster_colors_(self):
        """
        An in-place clustering of colors, replaces existing image with the quantized version
        """

        colors, labels, q_img = self.cluster_colors()
        q_img = (q_img * 255).astype(np.uint8)
        # print(q_img.dtype)

        self.setImage(q_img.copy())

    def get_num_clusters(self):
        """
        Algorithmically gets optimal number of clusters for k means using knee method

        Returns:
            numClusters: The optimal number of clusters found by the K Knee method
        """

        max_test = 25
        num_samples = 10000
        inertias = []
        x_vals = np.arange(1, max_test)
        for i in x_vals:
            # run on sample to save time for approximation
            image_arr_sample = shuffle(
                self.img1d, random_state=0, n_samples=num_samples
            )
            kmeans = KMeans(n_clusters=i, n_init="auto", random_state=random_state)
            kmeans.fit(image_arr_sample)
            inertia = kmeans.inertia_
            inertias.append(inertia)

        # plt.plot(x_vals, inertias)
        # plt.show()

        kn = KneeLocator(
            x=x_vals,
            y=inertias,
            curve="convex",
            direction="decreasing",
        )
        return kn.knee

    def plt_cluster_pie(self):
        """
        Plots a pie chart based on the percentage of each color in the image
        """

        unique_values, counts = np.unique(self.labels, return_counts=True)
        percentages = (counts / len(self.labels)) * 100
        # plt.pie(
        #     percentages,
        #     colors=np.array(self.palette),
        #     labels=np.arange(len(self.palette)),
        # )
        # plt.show()

    def resetImage(self):
        """
        Resets the existing image with the stored original image for easier testing of variants
        """

        self.setImage(self.originalImage.copy())

    def showImg(self, img=None, title="", figsize=(12, 12)):
        """
        A utility function to show the current image

        Arguments:
            title: The title for the plot
            figsize: The figure size of the image
        """

        displayImage = None
        if img is None:
            displayImage = self.getImage()
        else:
            displayImage = img

        # plt.figure(figsize=figsize)
        # plt.imshow(displayImage)
        # plt.title(title)
        # plt.show()

    def get1DImg(self, image: np.ndarray) -> np.ndarray:
        """
        Vectorizes a given image of shape (H, W, C) to shape (H*W, C)

        Arguments:
            image: The image to vectorize to 1 dimension

        Returns:
            A reshaped image vectorized over the channel axis.
        """

        H, W, C = image.shape
        return image.reshape((H * W, C))

    def setImage(self, img: np.ndarray):
        """
        Updates the currently stored image to img and updates the img1d class variable

        Arguments:
            img: The image that should replace the existing image. Will also update the 1d representation accordingly, but not clustering or other variables.
        """

        self.image = img.copy()
        self.img1d = self.get1DImg(self.image)

    def getImage(self) -> np.ndarray:
        """
        Returns a copy of the current image that can be stored or modified

        Returns:
            copy: A copy of the current self.image
        """

        return self.image.copy()

    def getImageArea(self) -> int:
        """
        Returns the image area

        Returns:
            area: H*W for an image of shape (H, W, C)
        """

        H, W, C = self.image.shape
        return H * W

    def resizeImage(
        self, image=None, scale: float = 1, dimension: tuple = None
    ) -> None:
        """
        Return a resized version of the provided image or self.image if image=None.

        Arguments:
            scale: A float > 0 that is used to scale the image up or down with a scale of 1 returning the same image.
            dimension=None: A tuple representing the manual size the image should be in the form (H, W). Overrides any given scale value.
        """

        assert scale > 0, f"Given scale {scale} must be greater than 0!"

        img = None
        if image is None:
            img = self.getImage().astype(np.uint8)
        else:
            img = image

        H, W = 0, 0

        if img.ndim == 3:
            H, W, C = img.shape
        elif img.ndim == 2:
            H, W = img.shape

        resized = None

        if dimension is not None:
            NH, NW = dimension

            # If upsampling, use INTER_NEAREST, otherwise, use INTER_AREA. We want to use INTER_NEAREST for upsampling to preserve the number of colors
            if (
                NH * NW >= H * W
            ):  # This is a crude estimate for up vs downsampling, but it works well enough
                resized = cv2.resize(img, (NW, NH), interpolation=cv2.INTER_NEAREST)
            else:
                resized = cv2.resize(img, (NW, NH), interpolation=cv2.INTER_AREA)
        else:
            NH, NW = int(H * scale), int(W * scale)

            if scale <= 1:
                resized = cv2.resize(img, (NW, NH), interpolation=cv2.INTER_AREA)
            else:
                resized = cv2.resize(img, (NW, NH), interpolation=cv2.INTER_NEAREST)

        return resized

    def resizeImage_(self, scale: float = 1, dimension: tuple = None) -> None:
        """
        Resize the stored image in place by some scale factor.

        Arguments:
            scale: A float > 0 that is used to scale the image up or down with a scale of 1 returning the same image.
            dimension=None: A tuple representing the manual size the image should be in the form (H, W). Overrides any given scale value.
        """

        resized = self.resizeImage(scale=scale, dimension=dimension)

        self.setImage(resized)

    def lower_resolution(self, max_pixels):
        img = self.getImage()
        h, w = img.shape[:2]

        if h * w <= max_pixels:
            return

        aspect_ratio = w / h

        downsampled_w = int((max_pixels * aspect_ratio) ** 0.5)
        downsampled_h = int(downsampled_w / aspect_ratio)
        downsized_image = cv2.resize(
            img, (downsampled_w, downsampled_h), interpolation=cv2.INTER_AREA
        )
        self.setImage(downsized_image)

    def blurImage_(
        self,
        blurType: str,
        ksize: int = 13,
        sigma: float = 3,
        sigmaColor: float = 21,
        sigmaSpace: float = 21,
    ) -> None:
        """
        Blurs the current image in place according to the arguments of the function.
        Updates self.image and self.img1d

        Arguments:
            blurType: 'gaussian', 'median', or 'bilateral'. Determines the kind of filter to be applied
            ksize: The size of the blurring kernel to be applied
            sigma: A sigma for the gaussian kernel type
            sigmaColor: How large of a range colors should be blended, higher values means more distant colors will be blended
            sigmaSpace: How intensely pixels in the kernel are blurred
        """

        image = self.image.astype(np.uint8)
        blurred = None

        if blurType == "gaussian":
            kernel = cv2.getGaussianKernel(ksize=ksize, sigma=sigma)
            blurred = cv2.filter2D(image, ddepth=-1, kernel=kernel)
            blurred = cv2.filter2D(image, ddepth=-1, kernel=kernel.T)
        elif blurType == "median":
            blurred = cv2.medianBlur(image, ksize=ksize)
        elif blurType == "bilateral":
            blurred = cv2.bilateralFilter(
                image, d=ksize, sigmaColor=sigmaColor, sigmaSpace=sigmaSpace
            )

        self.image = blurred
        self.img1d = self.get1DImg(self.image)

    def getUniqueColors(self, image=None) -> np.ndarray:
        """
        Gets an array of shape (N, 3) which represents all the unique colors present in self.image

        Arguments:
            image=None: If None, returns the unique colors of self.image, otherwise, performs the operations for the provided image.

        Returns:
            uniqueColors: A (N, 3) numpy array which represents the found unique colors in the provided or current image.
        """

        reshaped_image = None
        if image is None:
            # Reshape to a 2D array
            reshaped_image = self.image.reshape(-1, self.image.shape[2])
        else:
            reshaped_image = image.reshape(-1, image.shape[2])

        # Find unique color values across the channels
        uniqueColors = np.unique(reshaped_image, axis=0)

        return uniqueColors

    def getUniqueColorsMasks(self) -> dict:
        """
        Returns a dictionary with indices of each unique color and a binary numpy array representing where each unique color is
        a key and each value is a binary mask of the image representing where that color is.

        Returns:
            colorsDict: A dictionary with keys of RGB tuples and values of binary masks representing the presence of that key in the image
        """

        colorsDict = {}

        uniqueColors = self.getUniqueColors()

        for color in uniqueColors:
            colorsDict[tuple(color)] = np.repeat(
                np.all(self.image == color, axis=2)[..., np.newaxis], repeats=3, axis=2
            )

        self.colorMasks = colorsDict

        return colorsDict

    def generatePrunableClusters(self, showPlots=False):
        """
        Stores color masks in self.prunableClusters which can be pruned from the main image. The small pruned clusters can be replaced by the nearest color
        in the original image in a different function. The treshold used to determine which clusters should be removed is defined as self.pruningThreshold

        Arguments:
            showPlots=False: Whether or not to show plots of pruned clusters
        """

        colorsDict = self.getUniqueColorsMasks()

        prunableClusters = {}

        for color in colorsDict.keys():
            mask = colorsDict[color]

            # Convert color tuple to an array
            color = np.array(color, dtype=np.uint8)
            singleColorImage = color * mask

            # if showPlots:
            #     plt.imshow(singleColorImage), plt.title(color)
            #     plt.show()

            # The mask seems to need to be a "binary" image but the binary values are 0 and 255 instead of 0 and 1
            (
                numLabels,
                labels,
                stats,
                centroids,
            ) = cv2.connectedComponentsWithStatsWithAlgorithm(
                (mask[..., 0] * 255).astype(np.uint8), 8, cv2.CV_32S, cv2.CCL_WU
            )

            # if showPlots:
            #     plt.imshow(labels), plt.title("Before pruning")
            #     plt.show()

            labelIndices = np.arange(1, numLabels)
            areas = stats[labelIndices, -1]

            imageArea = self.getImageArea()
            # Get an array representing the clusters that are too small and should be pruned
            tooSmall = imageArea * self.pruningThreshold > areas
            # Negatable is an array containing the labels that should be pruned, these are then negated in the labels mask
            negatable = labelIndices[tooSmall]
            negateMask = np.isin(labels, negatable)
            labels[negateMask] *= -1

            # Convert from labels to a mask where each pruned cluster has its unique segmented label
            labels[labels > 0] = 0
            labels = -labels

            # if showPlots:
            #     plt.imshow(labels), plt.title("Pruned clusters")
            #     plt.show()

            prunableClusters[tuple(color)] = labels

            # if showPlots:
            #     binaryLabels = (labels > 0).astype(np.uint8)
            #     plt.imshow(mask[..., 0] - binaryLabels), plt.title("After pruning")
            #     plt.show()

        self.prunableClusters = prunableClusters

    def getMainSurroundingColor(self, image, mask) -> np.ndarray:
        """
        Returns the main surrounding color given a binary mask and image. The function will check the edges of the mask to determine the present colors
        and will return the most common color surrounding the mask.

        Arguments:
            image: The image to use as a reference for the surrounding colors
            mask: A binary mask which will be used to determine the cluster of pixels we want to find the common color around

        Returns:
            mostCommonColor: A (3,) numpy array which holds the RGB value of the most common color
        """

        assert image.shape[:-1] == mask.shape, "Image and mask shapes are different!"

        edgeFilter = np.array(([0, 1, 0], [1, -4, 1], [0, 1, 0]))

        maskEdges = cv2.filter2D(mask, ddepth=-1, kernel=edgeFilter)

        # plt.figure(figsize=(20, 20)), plt.imshow(maskEdges), plt.title('Small cluster edge'), plt.show()

        surroundingColors = image[maskEdges.astype(bool)]

        # most_common(1) returns a list with a single tuple (key, count)
        mostCommonColor = Counter(map(tuple, surroundingColors)).most_common(1)[0][0]
        return np.array(mostCommonColor, dtype=np.uint8)

    def getMainSurroundingColorVectorized(
        self, image, mask, uniqueLabels
    ) -> np.ndarray:
        """
        Returns the main surrounding colors given a labeled mask and image. The function will check the edges of the mask to determine the present colors
        and will return the most common color surrounding the mask.

        Arguments:
            image: The image to use as a reference for the surrounding colors
            mask: A 3D binary mask of shape (H, W, N) where N is the number of unique clusters excluding the background. The mask should be 1 where
                a certain unique label exists and 0 elsewhere.

        Returns:
            modeColors: A (N, 3) numpy array which holds the RGB values of the most common colors for each label
        """

        # assert image.shape[:-1] == mask.shape, 'Image and mask shapes are different!'

        edgeFilter = np.array(([0, 1, 0], [1, -4, 1], [0, 1, 0]), dtype=np.int32)

        modeColors = []
        for label in uniqueLabels:
            maskEdges = cv2.filter2D(
                (mask == label).astype(np.uint8), ddepth=-1, kernel=edgeFilter
            ).astype(bool)
            # plt.figure(figsize=(20, 20)), plt.imshow(maskEdges), plt.title('Small cluster edge'), plt.show()
            modeColors.append(
                Counter(map(tuple, image[maskEdges])).most_common(1)[0][0]
            )

        return np.array(modeColors, dtype=np.uint8)

    # TODO: If time allows, re-write this to merge similar intensities along strong gradients to preserve things like the whiskers in the Red Panda image
    def pruneClustersSmart(
        self,
        iterations: int = 3,
        pruneBySize=False,
        reversePruneBySize=False,
        reversePruneByIntensity=True,
        showPlots=False,
    ):
        """
        Prunes small color clusters in order of cluster size and color intensity. The pruned clusters are based on the self.pruningThreshold class variable
        and this function just determines the order that clusters are pruned to produce slightly different results.

        Arguments:
            iterations: How many times clusters are pruned by repeating this same function.
            pruneBySize=False: Whether prunable clusters should be pruned from smallest to largest. This has a large impact on performance if set to True.
                When set to False, the smart method is pretty much as fast as the simple method
            reversePruneBySize=False: By default, prunes clusters from smallest to largest. Set to True to prune by largest to smallest.
            reversePruneByIntensity=True: Whether clusters should be pruned based on color intensity in order from darkest to lightest by default.
            showPlots=False: Whether to show intermediate pruning plots for each iteration.
        """

        for i in range(iterations):
            self.generatePrunableClusters(showPlots=False)

            image = self.image.copy().astype(np.int32)
            prunableClusters = self.prunableClusters

            mergedColors = -np.ones_like(image, dtype=np.int32)

            # if showPlots:
            #     plt.figure(figsize=(20, 20)), plt.imshow(self.image), plt.title(
            #         "Before pruning"
            #     ), plt.show()

            colorsOrdered = sorted(
                prunableClusters.items(),
                key=lambda x: np.sum(np.array(x[0])) ** 2,
                reverse=reversePruneByIntensity,
            )

            for color, labelMask in colorsOrdered:
                color = np.array(color, dtype=np.uint8)

                uniqueLabels = np.unique(labelMask)[1:]

                # Get the labels in an order sorted by their patch size in the labelMask excluding the last element which is the background
                if pruneBySize:
                    uniqueLabels = np.array(
                        sorted(
                            uniqueLabels, key=lambda x: Counter(labelMask.flatten())[x]
                        )[:-1]
                    )
                    if reversePruneBySize:
                        uniqueLabels[::-1]

                # plt.figure(figsize=(20, 20)), plt.imshow(labelMask), plt.title('labelMask'), plt.show()

                # If no unique labels are detected, continue to the next color
                if uniqueLabels.shape[0] == 0:
                    continue

                surroundingColors = self.getMainSurroundingColorVectorized(
                    image, labelMask, uniqueLabels
                )

                # Create an index mapping for each unique label
                consistentIndexingMap = {
                    label: index for index, label in enumerate(uniqueLabels)
                }

                # Create an indexed version of labelMask for non-zero labels
                consistentLabelMask = np.zeros_like(labelMask)

                # Edit the current label mask so it has consistent integer values to quickly map them to colors
                for label, index in consistentIndexingMap.items():
                    consistentLabelMask[labelMask == label] = index

                # Apply the mapping only to non-zero labels
                image[labelMask != 0] = surroundingColors[
                    consistentLabelMask[labelMask != 0]
                ]

            # if showPlots:
            #     plt.figure(figsize=(20, 20)), plt.imshow(mergedColors), plt.title(
            #         "mergedColors"
            #     ), plt.show()

            #     mergedColorsMask = (mergedColors == -1).astype(np.uint8)
            #     plt.figure(figsize=(20, 20)), plt.imshow(
            #         mergedColorsMask * 255
            #     ), plt.title("mergedColorsMask"), plt.show()

            #     plt.figure(figsize=(20, 20)), plt.imshow(self.image), plt.title(
            #         "Before pruning"
            #     ), plt.show()
            #     # plt.figure(figsize=(20, 20)), plt.imshow(prunedImage), plt.title('After pruning'), plt.show()
            #     plt.figure(figsize=(20, 20)), plt.imshow(image), plt.title(
            #         "After pruning"
            #     ), plt.show()

            #     plt.figure(figsize=(20, 20)), plt.imshow(
            #         np.abs(self.image - image)
            #     ), plt.title("Diff"), plt.show()

            self.setImage(image.copy())

    def pruneClustersSimple(self, iterations: int = 3, showPlots=False):
        """
        A simple cluster pruning method which iteratively prunes the smallest clusters below the self.pruningThreshold class variable.
        In most cases, this simple method produces similar results to pruneClustersSmart(), but is faster.

        Arguments:
            iterations: How many times clusters are pruned by repeating this same function. A single iteration probably isn't
                guaranteed to remove all small clusters, so this function can be run any number of times to ensure all clusters are pruned
        """

        print(f"Starting pruning... \nIteration (of {iterations}): ", end="")

        for i in range(iterations):
            print(f"{i+1} ", end="")

            image = self.image.copy().astype(np.int32)
            # print('Starting generatePrunableClusters()')
            self.generatePrunableClusters(showPlots=False)
            # print('Done!')

            prunableClusters = self.prunableClusters

            # if showPlots:
            #     plt.figure(figsize=(20, 20)), plt.imshow(self.image), plt.title(
            #         "Before pruning"
            #     ), plt.show()

            # print('Starting pruning loop')
            for color, labelMask in prunableClusters.items():
                color = np.array(color, dtype=np.uint8)

                uniqueLabels = np.unique(labelMask)[
                    1:
                ]  # Exclude the first label which refers to the background

                # If no unique labels are detected, continue to the next color
                if uniqueLabels.shape[0] == 0:
                    continue

                surroundingColors = self.getMainSurroundingColorVectorized(
                    image, labelMask, uniqueLabels
                )

                # Create an index mapping for each unique label
                consistentIndexingMap = {
                    label: index for index, label in enumerate(uniqueLabels)
                }

                # Create an indexed version of labelMask for non-zero labels
                consistentLabelMask = np.zeros_like(labelMask)

                # Edit the current label mask so it has consistent integer values to quickly map them to colors
                for label, index in consistentIndexingMap.items():
                    consistentLabelMask[labelMask == label] = index

                # Apply the mapping only to non-zero labels
                image[labelMask != 0] = surroundingColors[
                    consistentLabelMask[labelMask != 0]
                ]

            # if showPlots:
            #     plt.figure(figsize=(20, 20)), plt.imshow(self.image), plt.title(
            #         "Before pruning"
            #     ), plt.show()
            #     plt.figure(figsize=(20, 20)), plt.imshow(image), plt.title(
            #         "After pruning"
            #     ), plt.show()

            #     plt.figure(figsize=(20, 20)), plt.imshow(
            #         np.abs(self.image - image)
            #     ), plt.title("Diff"), plt.show()

            self.setImage(image)

        print("\nDone!")

    def getBoundaryImage(
        self, image: np.ndarray = None, scale: float = 1
    ) -> np.ndarray:
        """
        Gets a boundary image between colors in a PBN template by running an edge filter on the provided image or self.image.
        Upscaling the image before passing it to this function gives better resolution.

        Arguments:
            image: An input image to get the edges of. Uses self.image if image is None
            scale: A value to scale the image by before applying the edge filter. Useful if you want higher resolution
                in the resulting boundary image for labeling regions.

        Returns:
            boundaryImage: A binary image that represents the boundaries found when applying the edge filter.
        """

        img = None
        if image is None:
            img = self.getImage().astype(np.uint8)
        else:
            img = image.copy().astype(np.uint8)

        edgeFilter = np.array(([0, 1, 0], [1, -4, 1], [0, 1, 0]))

        if scale != 1:
            img = self.resizeImage(image=img, scale=scale)

        boundaryImage = cv2.filter2D(img, ddepth=-1, kernel=edgeFilter)
        boundaryImage = np.sum(boundaryImage, axis=2)
        boundaryImage[boundaryImage > 0] = 1

        return boundaryImage

    def set_final_pbn(self, border_size=5):
        """
        Runs all necessary functions to get the final paint by number image
        and set the internal image representation to it.
        """
        # print("lowering resolution")
        # self.lower_resolution(self.max_resolution)

        print("clustering colors")
        self.cluster_colors_()

        img = self.getImage()
        h, w, c = img.shape
        canvas = np.zeros((h + 2 * border_size, w + 2 * border_size, c), dtype=np.uint8)
        canvas[border_size : border_size + h, border_size : border_size + w] = img
        self.setImage(canvas)

    def output_to_svg(self, output_palette_path: str = None):
        """
        Gets a boundary image between colors in a PBN template by running an edge filter on the provided image or self.image.
        Upscaling the image before passing it to this function gives better resolution.

        Arguments:
            svg_path: File path to output the svg to.
        Returns:
            palette: A dictionary of all colors in the image each with an array
            of unique html ids representing each shape. This will allow for javascript
            manipulation of the color of each shape.
        """
        print("writing contours to svg")
        img = self.getImage()
        h, w, c = img.shape
        min_area = h * w * self.min_percent_area

        dwg = svgwrite.Drawing(profile="tiny", viewBox=(f"0 0 {w} {h}"))
        i = 0
        palette = []
        color_masks = self.getUniqueColorsMasks()
        for idx, (color, mask) in enumerate(color_masks.items()):
            mask[mask == False] = 0
            mask[mask == True] = 1
            boundary_img = self.getBoundaryImage(mask)

            contours, hierarchy = cv2.findContours(
                boundary_img.astype(np.uint8),
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_TC89_L1,
            )

            data = {}
            data["color"] = str(color)
            data["shapes"] = []
            for c in contours:
                points = c.squeeze().tolist()
                if len(points) < 4:
                    continue

                polygon = Polygon([pt[0] for pt in c])
                if polygon.area < min_area:
                    continue

                fill = "white"
                group = dwg.g(fill=fill, stroke="black", id=str(i))
                shape = dwg.polygon(points)

                # add text label
                text = self.add_text_label(dwg, c, str(idx))

                group.add(shape)
                group.add(text)
                dwg.add(group)
                data["shapes"].append(str(i))
                i += 1

            palette.append(data)

        return dwg.tostring(), palette

    def point_inside_contour(self, point, contour):
        """Check if a point is inside a contour."""
        return cv2.pointPolygonTest(contour, (point[0], point[1]), False) >= 0

    def sample_text_position(self, contour, num_samples=150):
        # Convert contour to a shapely polygon for area computation
        polygon = Polygon([pt[0] for pt in contour])
        min_x, min_y, max_x, max_y = polygon.bounds
        best_point = (0, 0)
        max_distance = -1

        for _ in range(num_samples):
            x, y = random.uniform(min_x, max_x), random.uniform(min_y, max_y)
            point = Point(x, y)

            # Check if the sampled point is within the polygon and its distance to edges
            if polygon.contains(point):
                distance = polygon.exterior.distance(point)
                if distance > max_distance:
                    max_distance = distance
                    best_point = (x, y)

        return best_point

    def add_text_label(self, dwg, contour, label):
        best_point = self.sample_text_position(contour)

        # Estimate a suitable text size
        text_size = np.clip(np.sqrt(cv2.contourArea(contour)) / 8, 4, 12)

        text = dwg.text(
            label,
            insert=best_point,
            font_size=str(text_size),
            text_anchor="middle",
        )
        return text
