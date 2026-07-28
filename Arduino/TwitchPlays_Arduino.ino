const int zMotorPin1 = 8;
const int zMotorPin2 = 9;
const int yMotorPin1 = 10;
const int yMotorPin2 = 11;
const int xMotorPin1 = 12;
const int xMotorPin2 = 13;

const int fwdlimitSwitchPin = 2;
const int backlimitSwitchPin = 3;
const int leftlimitSwitchPin = 5;
const int rightlimitSwitchPin = 4;

const int delayTime = 1000;

void setup() {
  Serial.begin(9600);
  pinMode(zMotorPin1, OUTPUT);
  pinMode(zMotorPin2, OUTPUT);
  pinMode(yMotorPin1, OUTPUT);
  pinMode(yMotorPin2, OUTPUT);
  pinMode(xMotorPin1, OUTPUT);
  pinMode(xMotorPin2, OUTPUT);

  pinMode(fwdlimitSwitchPin, INPUT_PULLUP);
  pinMode(backlimitSwitchPin, INPUT_PULLUP);
  pinMode(leftlimitSwitchPin, INPUT_PULLUP);
  pinMode(rightlimitSwitchPin, INPUT_PULLUP);
}

void moveMotor(int highMotor, int lowMotor){
  digitalWrite(highMotor, HIGH);
  digitalWrite(lowMotor, LOW);
  delay(delayTime);
  digitalWrite(highMotor, LOW);
  digitalWrite(lowMotor, LOW);
}

void returnToOrigin(){
  while(digitalRead(leftlimitSwitchPin) == LOW){
    digitalWrite(yMotorPin1, LOW);
    digitalWrite(yMotorPin2, HIGH);
  }
  // turn off left motor
  digitalWrite(yMotorPin1, LOW);
  digitalWrite(yMotorPin2, LOW);
  // move back
  while(digitalRead(backlimitSwitchPin) == LOW){
  digitalWrite(xMotorPin1, LOW);
  digitalWrite(xMotorPin2, HIGH);
  }
  // turn off back motor
  digitalWrite(xMotorPin1, LOW);
  digitalWrite(xMotorPin2, LOW);
  // pause for next drop
  delay(1000);
}


void loop() {
  if (Serial.available() > 0) {
    // Read input until newline
    String input = Serial.readStringUntil('\n');
    input.trim();  // Remove any extra whitespace

    int leftLimit = digitalRead(leftlimitSwitchPin);
    int rightLimit = digitalRead(rightlimitSwitchPin);
    int backLimit = digitalRead(backlimitSwitchPin);
    int fwdLimit = digitalRead(fwdlimitSwitchPin);

    Serial.println(input);
    if (input == "left" && leftLimit == LOW) {
      moveMotor(yMotorPin2,yMotorPin1);
    } else if (input == "right" && rightLimit == LOW) {
      moveMotor(yMotorPin1,yMotorPin2);
    } else if (input == "back" && backLimit == LOW) {
      moveMotor(xMotorPin2,xMotorPin1);
    } else if (input == "fwd" && fwdLimit == LOW) {
      moveMotor(xMotorPin1,xMotorPin2);
    } else if (input == "down") {
      moveMotor(zMotorPin1,zMotorPin2);
    } else if (input == "up") {
      moveMotor(zMotorPin2,zMotorPin1);
    } else if (input == "return") {
      returnToOrigin();
    } else if (input == "grab") {
      // lower crane 
      digitalWrite(zMotorPin1, HIGH);
      digitalWrite(zMotorPin2, LOW);
      delay(3500);
      // pause crane
      digitalWrite(zMotorPin1, LOW);
      digitalWrite(zMotorPin2, LOW);
      delay(1000);
      // lift crane
      digitalWrite(zMotorPin1, LOW);
      digitalWrite(zMotorPin2, HIGH);
      delay(3500);
      // stop up/down motor
      digitalWrite(zMotorPin1, LOW);
      digitalWrite(zMotorPin2, LOW);
      // return to origin
      returnToOrigin();
      // lower crane 
      digitalWrite(zMotorPin1, HIGH);
      digitalWrite(zMotorPin2, LOW);
      delay(1500);
      // pause crane
      digitalWrite(zMotorPin1, LOW);
      digitalWrite(zMotorPin2, LOW);
      delay(1000);
      // lift crane
      digitalWrite(zMotorPin1, LOW);
      digitalWrite(zMotorPin2, HIGH);
      delay(1250);
      // stop up down motor
      digitalWrite(zMotorPin1, LOW);
      digitalWrite(zMotorPin2, LOW);
    }
    else {
      Serial.println("Invalid command.");
    }
    // safety to turn off all motors
    digitalWrite(zMotorPin1, LOW);
    digitalWrite(zMotorPin2, LOW);
    digitalWrite(yMotorPin1, LOW);
    digitalWrite(yMotorPin2, LOW);
    digitalWrite(xMotorPin1, LOW);
    digitalWrite(xMotorPin2, LOW);
  }
}