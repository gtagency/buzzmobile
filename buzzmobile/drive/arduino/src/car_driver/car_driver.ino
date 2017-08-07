#include <Arduino.h>
#include <Servo.h>
#include "pid.h"
#include <stdio.h>

const int enc_a      = 2;
const int motor_pin  = 3;
const int enc_b      = 4;
const int steer_pin  = 5;
const int estop_pin  = 6;
const int horn_pin   = 7;
const int yellow_led = 8;
const int red_led    = 13;
const int pot_pin    = A0;
const int brake_pin = 9;
const int brake_pot_pin = A1;

Servo motor;
Servo steer;
Servo brake;

int currentBrake;
int desiredBrake = 1;


volatile int ticks = 0;
volatile int count = 0;

const double ticksPerRev = 3600;
const double wheelCirc = 2.198;

const int minPotVal = 567;
const int maxPotVal = 740;
const int midPotVal = 660;
const float anglePerPotTick = 0.003697731; // rad

const int brakedPosition = 0;
const int unbrakedPosition = 1;

float desiredSpeed = 0; // m/s
float desiredAngle = 0; // rad
float lastSpeed = 0; // m/s

long lastTime;

PDController speedController(2, -0.1);
PDController steerController(15, -7.5);

long lastCmdTime;

float getSpeed() {
  float dTime = (millis() - lastTime) / 1000.0;
  lastTime = millis();
  float measured = 0;
  if(dTime > 0.001) {
    measured = ((ticks / ticksPerRev) * wheelCirc) / dTime;
    ticks = 0;
  } else {
    measured = lastSpeed;
  }

  lastSpeed = measured;
  return measured;
}

float getSteeringAngle() {
  return -1 * anglePerPotTick * (analogRead(pot_pin) - midPotVal);
}

void stopAll() {
  speedController.setDesiredValue(0);
  speedController.setOutput(90);
  motor.write(90);
  steerController.setDesiredValue(getSteeringAngle());
  steerController.setOutput(90);
  steer.write(90);
  digitalWrite(horn_pin, LOW);
}

void setup() {
  Serial.begin(9600);

  pinMode(motor_pin, OUTPUT);
  pinMode(steer_pin, OUTPUT);
  pinMode(enc_a, INPUT);
  pinMode(enc_b, INPUT);
  pinMode(red_led, OUTPUT);
  pinMode(yellow_led, OUTPUT);
  pinMode(horn_pin, OUTPUT);
  pinMode(estop_pin, INPUT);
  pinMode(brake_pin, OUTPUT);
  pinMode(brake_pot_pin, INPUT);
  
  lastTime = millis();
  
  attachInterrupt(0, onEncChange, CHANGE);
  
  motor.attach(motor_pin);
  steer.attach(steer_pin);
  brake.attach(brake_pin);
  
  speedController.setOutput(90);
  steerController.setOutput(90);
  speedController.setRange(0, 180);
  steerController.setRange(30, 150);
  speedController.setDesiredValue(0);
  steerController.setDesiredValue(0);
  
  digitalWrite(red_led, LOW);
  digitalWrite(yellow_led, LOW);
  digitalWrite(horn_pin, LOW);
}

void loop() {
  digitalWrite(yellow_led, digitalRead(estop_pin));
  
  char retMsg[20] = {0};
  if(Serial.available()) {
    if(Serial.read() == '$') {

      float newSpeed = Serial.parseFloat();
      speedController.setDesiredValue(newSpeed);
      steerController.setDesiredValue(Serial.parseFloat());
      desiredBrake = (abs(newSpeed) <= 0.01 ? 1 : Serial.parseInt());
      digitalWrite(horn_pin, Serial.parseInt());
      
      lastCmdTime = millis();
      char steeringStr[5] = {0};
      char speedStr[5] = {0};
      dtostrf(getSteeringAngle(), 5, 3, steeringStr);
      dtostrf(getSpeed(), 5, 3, speedStr);
      updateBrake();
      sprintf(retMsg, "$%05i,%s,%s", count, steeringStr, speedStr);
      Serial.println(retMsg);
      count = 0;
    }
  }
  
  /* Only run the controllers if the motors are enabled.
   * This prevents the controllers ramping up while the
   * vehicle is estopped, creating a dangerous situation.
   */
  if(digitalRead(estop_pin) == HIGH) {
    speedController.update(getSpeed());
    motor.write(speedController.getOutput());
    
    steerController.update(getSteeringAngle());
    // Soft limits on steering to avoid damage.
    if(analogRead(pot_pin) >= maxPotVal && steerController.getOutput() < 90)
      steer.write(90);
    else if(analogRead(pot_pin) <= minPotVal && steerController.getOutput() > 90)
      steer.write(90);
    else
      steer.write(steerController.getOutput());
      
    
    if(millis() - lastCmdTime > 500) {
      digitalWrite(red_led, HIGH);
      stopAll();
    } else {
      digitalWrite(red_led, LOW);
    }
  } else {
    // If estop is triggered, go ahead and reset the controllers.
    stopAll();
  }
  
  delay(50);
}

void onEncChange() {
  if(digitalRead(enc_a) == digitalRead(enc_b)) { 
    ticks--;
    count--;
  } else {
    ticks++;
    count++;
  }
}

void updateBrake() {
  if (analogRead(brake_pot_pin) >= brakedPosition) {
    currentBrake = 1; 
  } else if (analogRead(brake_pot_pin) <= unbrakedPosition) {
    currentBrake = 0;
  }
  if (desiredBrake == 1 && currentBrake != 1) {
    brake.write(180);
  } else if (desiredBrake == 0 && currentBrake != 0) {      
    brake.write(0);     
  } else if (desiredBrake == currentBrake) {
    brake.write(0);
  }
}


