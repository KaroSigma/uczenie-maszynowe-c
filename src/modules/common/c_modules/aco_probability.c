#include <math.h>

void calculate_probabilities(double* probabilities, 
                            double* pheromones, 
                            double* distances,
                            int n_points,
                            double alpha,
                            double beta) {
    double total = 0.0;
    
    for(int i = 0; i < n_points; i++) {
        double prob = pow(pheromones[i], alpha) * pow(1.0/(distances[i] + 1e-6), beta);
        probabilities[i] = prob;
        total += prob;
    }
    
    // Normalizacja
    for(int i = 0; i < n_points; i++) {
        probabilities[i] /= total;
    }
}