#include <iostream>
using namespace std;
int main(){
	int a11, a12, a21, a22, x, y;
	cin >> a11 >> a12 >> a21 >> a22 >> x >> y;
	cout << a11*x+a12*y << " " << a21*x-a22*y;
}