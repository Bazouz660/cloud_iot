#include <WiFi.h>
#include <HTTPClient.h>
#include "driver/i2s.h"

// WiFi & server configuration
const char* ssid = "MIWIFI_E444";
const char* password = "246J9F4K";
const char* serverUrl = "http://192.168.1.134:5000/api/audio";

// I2S microphone pin definitions
#define I2S_MIC_WS   15
#define I2S_MIC_SCK  14
#define I2S_MIC_SD   32

#define SAMPLE_RATE 16000
#define BUFFER_SIZE 256        // Number of 32-bit samples per I2S read
#define BATCH_SIZE  10         // Number of buffers to batch before sending

// Global buffer to accumulate binary samples
std::vector<int16_t> audioBatch;

void setupI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,  // Capture 32-bit samples
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
    .intr_alloc_flags = 0,
    .dma_buf_count = 4,
    .dma_buf_len = BUFFER_SIZE,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_MIC_SCK,
    .ws_io_num = I2S_MIC_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_MIC_SD
  };

  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  i2s_zero_dma_buffer(I2S_NUM_0);
}

void sendBatch() {
  if (audioBatch.empty()) return;
  
  // Send raw binary data. You could also add headers for sample rate etc.
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/octet-stream");
  
  // Convert vector to byte array
  size_t dataSize = audioBatch.size() * sizeof(int16_t);
  uint8_t* data = (uint8_t*)audioBatch.data();
  
  int httpResponseCode = http.POST(data, dataSize);
  if (httpResponseCode > 0) {
    Serial.print("Batch sent, response code: ");
    Serial.println(httpResponseCode);
  } else {
    Serial.print("Error sending batch: ");
    Serial.println(httpResponseCode);
  }
  http.end();
  audioBatch.clear();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting ESP32 Audio Streaming...");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi.");
  setupI2S();
}

void loop() {
  int32_t i2sBuffer[BUFFER_SIZE];
  size_t bytesRead = 0;
  
  esp_err_t result = i2s_read(I2S_NUM_0, i2sBuffer, sizeof(i2sBuffer), &bytesRead, 1000);
  if (result == ESP_OK && bytesRead > 0) {
    int samplesRead = bytesRead / 4;
    // Append converted 16-bit samples to the batch buffer
    for (int i = 0; i < samplesRead; i++) {
      int16_t sample = i2sBuffer[i] >> 16;
      audioBatch.push_back(sample);
    }
  }
  
  // Once we've accumulated a full batch, send it
  if (audioBatch.size() >= (BUFFER_SIZE * BATCH_SIZE)) {
    sendBatch();
  }
  
  // Avoid a tight loop (tweak delay as needed)
  delay(10);
}
