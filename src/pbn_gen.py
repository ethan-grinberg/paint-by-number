import cv2
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from kneed import KneeLocator
from sklearn.utils import shuffle

# Change me to an integer for consistent results between runs, or set to None to allow randomness in K-means
random_state = None

class PbnGen:
    def __init__(self, f_name, num_colors=None, min_num_colors=10, pruningThreshold=6.25e-5):
        bgr_image = cv2.imread(f_name)
        # change to RGB
        rgbImage = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        
        # Retain an original image copy for easy testing
        self.originalImage = rgbImage
        self.originalImg1d = self.get1DImg(self.originalImage)
        
        # Set the actual working image to a copy of the original
        self.setImage(self.originalImage.copy())
        
        # The minimum percentage of the image's area a color cluster can be before getting absorbed by surrounding colors
        self.pruningThreshold = pruningThreshold
        
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

    def cluster_colors(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        
        """
        Performs K means clustering on the image to quantize it to a fixed number of colors.

        Returns:
            (palette, labels, q_img)
            
            palette: A (N, 3) numpy array representing the quantized colors in a float32 format.
            labels: A (H*W,) numpy array which holds the assigned labels for each pixel in the image.
            q_img: A (H, W, 3) quantized image which holds the original image quantized to the specified number of colors.
        """
        
        model = KMeans(n_clusters=self.num_colors, n_init="auto", random_state=random_state)
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
        q_img = (q_img*255).astype(np.uint8)
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
        plt.pie(
            percentages,
            colors=np.array(self.palette),
            labels=np.arange(len(self.palette)),
        )
        plt.show()

    def resetImage(self):
        
        """
        Resets the existing image with the stored original image for easier testing of variants
        """
        
        self.setImage(self.originalImage.copy())

    def showImg(self, title='', figsize=(12, 12)):
        
        """
        A utility function to show the current image
        
        Arguments:
            title: The title for the plot
            figsize: The figure size of the image
        """
        
        plt.figure(figsize=figsize)
        plt.imshow(self.image), plt.title(title)
        plt.show()

    def get1DImg(self, image: np.ndarray) -> np.ndarray:
        
        """
        Vectorizes a given image of shape (H, W, C) to shape (H*W, C)

        Arguments:
            image: The image to vectorize to 1 dimension

        Returns:
            A reshaped image vectorized over the channel axis.
        """
        
        H, W, C = image.shape
        return image.reshape((H*W, C))

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
        return H*W
    
    def resizeImage_(self, scale:float=1, dimension:tuple=None) -> None:
        
        """
        Resize the stored image in place by some scale factor.
        
        Arguments:
            scale: A float > 0 that is used to scale the image up or down with a scale of 1 returning the same image.
            dimension=None: A tuple representing the manual size the image should be in the form (H, W). Overrides any given scale value.
        """
        
        assert scale > 0, f'Given scale {scale} must be greater than 0!'
        
        img = self.getImage().astype(np.uint8)
        H, W, C = img.shape

        resized = None
        
        if dimension is not None:
            NH, NW = dimension
            
            # If upsampling, use INTER_NEAREST, otherwise, use INTER_AREA. We want to use INTER_NEAREST for upsampling to preserve the number of colors
            if NH*NW >= H*W: # This is a crude estimate for up vs downsampling, but it works well enough
                resized = cv2.resize(img, (NW, NH), interpolation = cv2.INTER_NEAREST) 
            else:
                resized = cv2.resize(img, (NW, NH), interpolation = cv2.INTER_AREA)
        else:
            NH, NW = int(H*scale), int(W*scale)

            if scale <= 1:
                resized = cv2.resize(img, (NW, NH), interpolation = cv2.INTER_AREA)
            else:
                resized = cv2.resize(img, (NW, NH), interpolation = cv2.INTER_NEAREST)
            
        self.setImage(resized)

    def blurImage_(self, blurType:str, ksize:int=13, sigma:float=3, sigmaColor:float=21, sigmaSpace:float=21) -> None:
        
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
        
        
        if blurType == 'gaussian':
            kernel = cv2.getGaussianKernel(ksize=ksize, sigma=sigma)
            blurred = cv2.filter2D(image, ddepth=-1, kernel=kernel)
            blurred = cv2.filter2D(image, ddepth=-1, kernel=kernel.T)
        elif blurType == 'median':
            blurred = cv2.medianBlur(image, ksize=ksize)
        elif blurType == 'bilateral':
            blurred = cv2.bilateralFilter(image, d=ksize, sigmaColor=sigmaColor, sigmaSpace=sigmaSpace)
                
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
            colorsDict[tuple(color)] = np.repeat(np.all(self.image == color, axis=2)[..., np.newaxis], repeats=3, axis=2)
            
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
            
            if showPlots:
                plt.imshow(singleColorImage), plt.title(color)
                plt.show()
            
            # The mask seems to need to be a "binary" image but the binary values are 0 and 255 instead of 0 and 1
            numLabels, labels, stats, centroids = cv2.connectedComponentsWithStatsWithAlgorithm(
                (mask[..., 0]*255).astype(np.uint8), 8, cv2.CV_32S, cv2.CCL_WU
            )
            
            if showPlots:
                plt.imshow(labels), plt.title('Before pruning')
                plt.show()
            
            labelIndices = np.arange(1, numLabels)
            areas = stats[labelIndices, -1]
            
            imageArea = self.getImageArea()
            # Get an array representing the clusters that are too small and should be pruned
            tooSmall = imageArea*self.pruningThreshold > areas
            # Negatable is an array containing the labels that should be pruned, these are then negated in the labels mask
            negatable = labelIndices[tooSmall]
            negateMask = np.isin(labels, negatable)
            labels[negateMask] *= -1

            # Convert from labels to a mask where each pruned cluster has its unique segmented label
            labels[labels > 0] = 0
            labels = -labels
            
            if showPlots:
                plt.imshow(labels), plt.title('Pruned clusters')
                plt.show()
            
            prunableClusters[tuple(color)] = labels
            
            if showPlots:
                binaryLabels = (labels > 0).astype(np.uint8)
                plt.imshow(mask[...,0]-binaryLabels), plt.title('After pruning')
                plt.show()
            
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
        
        assert image.shape[:-1] == mask.shape, 'Image and mask shapes are different!'
        
        edgeFilter = np.array((
            [0, 1, 0],
            [1, -4, 1],
            [0, 1, 0]
        ))
        
        maskEdges = cv2.filter2D(mask, ddepth=-1, kernel=edgeFilter)
        
        # plt.figure(figsize=(20, 20)), plt.imshow(maskEdges), plt.title('Small cluster edge'), plt.show()
        
        surroundingColors = image[maskEdges.astype(bool)]
        
        # most_common(1) returns a list with a single tuple (key, count)
        mostCommonColor = Counter(map(tuple, surroundingColors)).most_common(1)[0][0]
        return np.array(mostCommonColor, dtype=np.uint8)
    
    def getMainSurroundingColorVectorized(self, image, mask, uniqueLabels) -> np.ndarray:
        
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
        
        edgeFilter = np.array((
            [0, 1, 0],
            [1, -4, 1],
            [0, 1, 0]
        ), dtype=np.int32)
        
        
        modeColors = []
        for label in uniqueLabels:
            
            maskEdges = cv2.filter2D((mask == label).astype(np.uint8), ddepth=-1, kernel=edgeFilter).astype(bool)
            # plt.figure(figsize=(20, 20)), plt.imshow(maskEdges), plt.title('Small cluster edge'), plt.show()
            modeColors.append(Counter(map(tuple, image[maskEdges])).most_common(1)[0][0])

        return np.array(modeColors, dtype=np.uint8)


    # TODO: If time allows, re-write this to merge similar intensities along strong gradients to preserve things like the whiskers in the Red Panda image
    def pruneClustersSmart(self, iterations:int=3, pruneBySize=False, reversePruneBySize=False, reversePruneByIntensity=True, showPlots=False):
        
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
            
            if showPlots:
                plt.figure(figsize=(20, 20)), plt.imshow(self.image), plt.title('Before pruning'), plt.show()

            colorsOrdered = sorted(prunableClusters.items(), key=lambda x: np.sum(np.array(x[0]))**2, reverse=reversePruneByIntensity)
            
            for color, labelMask in colorsOrdered:
                
                color = np.array(color, dtype=np.uint8)
                
                uniqueLabels = np.unique(labelMask)[1:]
                
                # Get the labels in an order sorted by their patch size in the labelMask excluding the last element which is the background
                if pruneBySize:
                    uniqueLabels = np.array(sorted(uniqueLabels, key=lambda x: Counter(labelMask.flatten())[x])[:-1])
                    if reversePruneBySize:
                        uniqueLabels[::-1]
                
                
                # plt.figure(figsize=(20, 20)), plt.imshow(labelMask), plt.title('labelMask'), plt.show()
            
                # If no unique labels are detected, continue to the next color
                if uniqueLabels.shape[0] == 0:
                    continue

                surroundingColors = self.getMainSurroundingColorVectorized(image, labelMask, uniqueLabels)

                # Create an index mapping for each unique label
                consistentIndexingMap = {label: index for index, label in enumerate(uniqueLabels)}

                # Create an indexed version of labelMask for non-zero labels
                consistentLabelMask = np.zeros_like(labelMask)

                # Edit the current label mask so it has consistent integer values to quickly map them to colors
                for label, index in consistentIndexingMap.items():
                    consistentLabelMask[labelMask == label] = index

                # Apply the mapping only to non-zero labels
                image[labelMask != 0] = surroundingColors[consistentLabelMask[labelMask != 0]]
                    
            if showPlots:
                plt.figure(figsize=(20, 20)), plt.imshow(mergedColors), plt.title('mergedColors'), plt.show()
                
                mergedColorsMask = (mergedColors == -1).astype(np.uint8)
                plt.figure(figsize=(20, 20)), plt.imshow(mergedColorsMask*255), plt.title('mergedColorsMask'), plt.show()

                plt.figure(figsize=(20, 20)), plt.imshow(self.image), plt.title('Before pruning'), plt.show()
                # plt.figure(figsize=(20, 20)), plt.imshow(prunedImage), plt.title('After pruning'), plt.show()
                plt.figure(figsize=(20, 20)), plt.imshow(image), plt.title('After pruning'), plt.show()

                plt.figure(figsize=(20, 20)), plt.imshow(np.abs(self.image-image)), plt.title('Diff'), plt.show()
            
            self.setImage(image.copy())
        
    def pruneClustersSimple(self, iterations:int=3, showPlots=False):
        
        """
        A simple cluster pruning method which iteratively prunes the smallest clusters below the self.pruningThreshold class variable.
        In most cases, this simple method produces similar results to pruneClustersSmart(), but is faster.
        
        Arguments:
            iterations: How many times clusters are pruned by repeating this same function. A single iteration probably isn't
                guaranteed to remove all small clusters, so this function can be run any number of times to ensure all clusters are pruned
        """
    
        print(f'Starting pruning... \nIteration (of {iterations}): ', end='')
    
        for i in range(iterations):
            
            print(f'{i+1} ', end='')
            
            image = self.image.copy().astype(np.int32)
            # print('Starting generatePrunableClusters()')
            self.generatePrunableClusters(showPlots=False)
            # print('Done!')

            prunableClusters = self.prunableClusters
            
            if showPlots:
                plt.figure(figsize=(20, 20)), plt.imshow(self.image), plt.title('Before pruning'), plt.show()

            # print('Starting pruning loop')
            for color, labelMask in prunableClusters.items():
                
                color = np.array(color, dtype=np.uint8)
                
                uniqueLabels = np.unique(labelMask)[1:] # Exclude the first label which refers to the background
                
                # If no unique labels are detected, continue to the next color
                if uniqueLabels.shape[0] == 0:
                    continue

                surroundingColors = self.getMainSurroundingColorVectorized(image, labelMask, uniqueLabels)

                # Create an index mapping for each unique label
                consistentIndexingMap = {label: index for index, label in enumerate(uniqueLabels)}

                # Create an indexed version of labelMask for non-zero labels
                consistentLabelMask = np.zeros_like(labelMask)

                # Edit the current label mask so it has consistent integer values to quickly map them to colors
                for label, index in consistentIndexingMap.items():
                    consistentLabelMask[labelMask == label] = index

                # Apply the mapping only to non-zero labels
                image[labelMask != 0] = surroundingColors[consistentLabelMask[labelMask != 0]]
                
            if showPlots:                
                plt.figure(figsize=(20, 20)), plt.imshow(self.image), plt.title('Before pruning'), plt.show()
                plt.figure(figsize=(20, 20)), plt.imshow(image), plt.title('After pruning'), plt.show()

                plt.figure(figsize=(20, 20)), plt.imshow(np.abs(self.image-image)), plt.title('Diff'), plt.show()
            
            self.setImage(image)

        print('\nDone!')
    
