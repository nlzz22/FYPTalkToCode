#include <stdio.h>

int maxInArray(int[], int);

int main(void) {
	int arr[]  = {2,3,5,1,9,2,3,4};

	int num = maxInArray(arr, 8);
	printf("%d\n", num);
	
	return 0;
}

int maxInArray(int arr[], int size) {
	int max = arr[0];
	int i;

	for (i=1; i<size; i++) {
		if (arr[i] > max) {
			max = arr[i];
		}
	}

	return max;
}


