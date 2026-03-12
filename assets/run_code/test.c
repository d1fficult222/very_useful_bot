#include <stdio.h>
int main(){
    int a11, a12, a21, a22, x, y;
    scanf("%d %d %d %d %d %d", &a11, &a12, &a21, &a22, &x, &y);
    printf("%d %d", a11*x+a12*y, a21*x+a22*y);
}