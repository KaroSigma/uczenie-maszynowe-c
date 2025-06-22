#include <math.h>

double point_distance(int x1, int y1, int x2, int y2) {
    long dx = x2 - x1;
    long dy = y2 - y1;
    return sqrt(dx*dx + dy*dy);
}