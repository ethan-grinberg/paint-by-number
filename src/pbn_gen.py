import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from kneed import KneeLocator
from sklearn.utils import shuffle


class PbnGen:
    def __init__(self, f_name, num_colors=None, min_num_colors=10):
        bgr_image = cv2.imread(f_name)
        # change to RGB
        self.image = bgr_image[:, :, [2, 1, 0]]
        self.img1d = self.image.reshape(
            (self.image.shape[0] * self.image.shape[1], self.image.shape[2])
        )
        self.num_colors = num_colors if num_colors else self.get_num_clusters()
        # make sure number of colors is at least minimum number
        self.num_colors = (
            self.num_colors + min_num_colors
            if self.num_colors < min_num_colors
            else self.num_colors
        )
        print(f"Quantized to {self.num_colors} colors")

    def cluster_colors(self):
        model = KMeans(n_clusters=self.num_colors, n_init="auto")
        model.fit(self.img1d)

        # get primary colors as floats from 0 to 1
        self.palette = model.cluster_centers_ / 255
        self.labels = model.labels_
        # get quantized image
        q_img = self.palette[self.labels].reshape(self.image.shape)
        return self.palette, self.labels, q_img

    # algorithmically gets optimal number of clusters for k means using knee method
    def get_num_clusters(self):
        max_test = 25
        num_samples = 10000
        inertias = []
        x_vals = np.arange(1, max_test)
        for i in x_vals:
            # run on sample to save time for approximation
            image_arr_sample = shuffle(
                self.img1d, random_state=0, n_samples=num_samples
            )
            kmeans = KMeans(n_clusters=i, n_init="auto")
            kmeans.fit(image_arr_sample)
            inertia = kmeans.inertia_
            inertias.append(inertia)

        plt.plot(x_vals, inertias)
        plt.show()

        kn = KneeLocator(
            x=x_vals,
            y=inertias,
            curve="convex",
            direction="decreasing",
        )
        return kn.knee

    def plt_cluster_pie(self):
        unique_values, counts = np.unique(self.labels, return_counts=True)
        percentages = (counts / len(self.labels)) * 100
        plt.pie(
            percentages,
            colors=np.array(self.palette),
            labels=np.arange(len(self.palette)),
        )
        plt.show()
