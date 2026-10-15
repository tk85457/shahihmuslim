import java.util.Properties
import java.io.FileInputStream

plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

val keystorePropertiesFile = rootProject.file("key.properties")
val keystoreProperties = Properties()
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

android {
    namespace = "app.shahihmuslim"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = "28.2.13676358"

    compileOptions {
        isCoreLibraryDesugaringEnabled = true
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "app.shahihmuslim"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    signingConfigs {
        create("release") {
            keyAlias = keystoreProperties.getProperty("keyAlias") as String?
            keyPassword = keystoreProperties.getProperty("keyPassword") as String?
            val storeFilePath = keystoreProperties.getProperty("storeFile") as String?
            if (storeFilePath != null) {
                storeFile = rootProject.file(storeFilePath)
            }
            storePassword = keystoreProperties.getProperty("storePassword") as String?
        }
    }

    packaging {
        jniLibs {
            useLegacyPackaging = false
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

}

flutter {
    source = "../.."
}

dependencies {
    implementation("androidx.activity:activity-ktx:1.11.0")
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")

    // Google Mobile Ads Mediation Adapters & SDKs
    // Unity Ads SDK + Official Google AdMob Adapter
    implementation("com.unity3d.ads:unity-ads:4.13.1")
    implementation("com.google.ads.mediation:unity:4.13.1.0")
    implementation("com.google.ads.mediation:facebook:6.18.0.0")
}

// --- 16 KB page size fix -----------------------------------------------
// shared_preferences_android (pulled in transitively by the shared_preferences
// plugin) bundles androidx.datastore, whose libdatastore_shared_counter.so is
// only 16-KB-page-safe in datastore 1.1.7. Newer 1.2.x re-introduced an
// unaligned .so, so we pin every datastore artifact to 1.1.7 explicitly.
// See: https://github.com/flutter/flutter/issues/182898
configurations.all {
    resolutionStrategy {
        force("androidx.datastore:datastore:1.1.7")
        force("androidx.datastore:datastore-android:1.1.7")
        force("androidx.datastore:datastore-core:1.1.7")
        force("androidx.datastore:datastore-core-android:1.1.7")
        force("androidx.datastore:datastore-preferences:1.1.7")
        force("androidx.datastore:datastore-preferences-android:1.1.7")
        force("androidx.datastore:datastore-preferences-core:1.1.7")
    }
}
