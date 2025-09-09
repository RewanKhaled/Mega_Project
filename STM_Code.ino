float readTemp();
long readUltrasonic();

// Pins
#define LDR_PIN      PA5
#define TEMP_PIN     PA6
#define TRIG_PIN     PA7
#define ECHO_PIN     PB0
#define SERVO_PIN    PB11
#define RED1_PIN     PB7
#define RED2_PIN     PB6
#define RED3_PIN     PB5
#define GREEN_PIN    PB4
#define WHITE_PIN    PB3

// Objects
Servo radarServo;

// Variables
int servoAngle = 0;
int servoStep = 2;

// Setup
void setup() {
    Serial.begin(9600);

    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    pinMode(RED1_PIN, OUTPUT);
    pinMode(RED2_PIN, OUTPUT);
    pinMode(RED3_PIN, OUTPUT);

    pinMode(GREEN_PIN, OUTPUT);
    pinMode(WHITE_PIN, OUTPUT);

    radarServo.attach(SERVO_PIN);
    radarServo.write(0);
}

// Main Loop
void loop() {
    // Temperature
    float temperature = readTemp();
    if (temperature < 20) {
        digitalWrite(RED1_PIN, HIGH);
        digitalWrite(RED2_PIN, LOW);
        digitalWrite(RED3_PIN, LOW);
    } else if (temperature >= 20 && temperature <= 30) {
        digitalWrite(RED1_PIN, HIGH);
        digitalWrite(RED2_PIN, HIGH);
        digitalWrite(RED3_PIN, LOW);
    } else {
        digitalWrite(RED1_PIN, HIGH);
        digitalWrite(RED2_PIN, HIGH);
        digitalWrite(RED3_PIN, HIGH);
    }

    // LDR
    int ldrVal = analogRead(LDR_PIN);
    if (ldrVal < 500) // threshold → tune as needed
        digitalWrite(WHITE_PIN, HIGH);
    else
        digitalWrite(WHITE_PIN, LOW);

    // Ultrasonic
    long distance = readUltrasonic();
    if (distance > 0 && distance < 50)
        digitalWrite(GREEN_PIN, HIGH);
    else
        digitalWrite(GREEN_PIN, LOW);

    // Servo Sweep 
    radarServo.write(servoAngle);
    servoAngle += servoStep;
    if (servoAngle >= 180 || servoAngle <= 0)
        servoStep = -servoStep;

    // Serial Debug 
    Serial.print("Temp: ");
    Serial.print(temperature);
    Serial.print(" C | LDR: ");
    Serial.print(ldrVal);
    Serial.print(" | Distance: ");
    Serial.print(distance);
    Serial.println(" cm");

    delay(20);
}

// Helper Functions
float readTemp() {
    int val = analogRead(TEMP_PIN);
    float voltage = val * 5.0 / 1023.0;
    float tC = (voltage - 0.5) * 100.0; // TMP36
    return tC;
}

long readUltrasonic() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(5);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH);
    if (duration == 0) return -1;
    long distance = duration * 0.034 / 2;
    return distance;
}