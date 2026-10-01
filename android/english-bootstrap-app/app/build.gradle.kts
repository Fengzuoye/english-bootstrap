plugins {
    id("com.android.application")
}
android {
    namespace = "com.example.bootstrapreader"
    compileSdk = 34
    defaultConfig {
        applicationId = "com.example.bootstrapreader"
        minSdk = 24
        targetSdk = 34
        versionCode = 14
        versionName = "1.4"
    }
    buildTypes {
        release { isMinifyEnabled = false }
    }
}
