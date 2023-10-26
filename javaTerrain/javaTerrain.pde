
int w = 2400;
int h = 2400;
int cols;
int rows;
int factor = 20;
float[][] terrain;

float f = 0;

void setup() {
    size(800, 800, P3D);
    cols = w / factor;
    rows = h / factor;
    terrain = new float[rows][cols];
    
}

void draw() {

    f += 0.01;

    float yoff = f;
    for(int y = 0; y < rows; y++) {
        float xoff = 0.1;
        for(int x = 0; x < cols; x++) {
            terrain[y][x] = map(noise(xoff, yoff), 0, 1, -150, 150);
            xoff += 0.1;
        }
        yoff += 0.1;
    }

    background(0);
    stroke(255);
    noFill();

    translate(width / 2, height / 2);
    rotateX(PI / 3);
    translate(-w / 2, -h / 2);

    for(int y = 0; y < rows - 1; y++) {
        beginShape(TRIANGLE_STRIP);
        for(int x = 0; x < cols; x++) {
            vertex(x * factor, y * factor, terrain[y][x]);
            vertex(x * factor, (y + 1) * factor, terrain[y + 1][x]);
            // rect(x * factor, y * factor, factor, factor);
        }
        endShape();
    }
    

    
}
