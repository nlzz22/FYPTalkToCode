#include <stdio.h>

int findMaximum(int[], int);

int main(void) {
	int arr[]  = {2,3,5,1,9,2,3,4};

	int num = findMaximum(arr, 8);
	printf("%d\n", num);
	
	return 0;
}

int findMaximum(int numbers[], int length) {
	int max = numbers [0];
	int i;

	for (i = 1; i < length; i++) {
		if (numbers [i] > max) {
			max = numbers [i];
		}
	}

	return max;
}



