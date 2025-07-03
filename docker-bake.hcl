// Variables with defaults that can be overridden
variable "REGISTRY" {
  default = "ghcr.io"
}

variable "IMAGE_NAME" {
  default = "sygaldry"
}

variable "TAG" {
  default = "latest"
}

// Base target with shared configuration
target "docker-metadata-action" {
  tags = [
    "${REGISTRY}/${IMAGE_NAME}:${TAG}",
    "${REGISTRY}/${IMAGE_NAME}:latest",
  ]
}

// Default target that extends the base
target "build" {
  inherits = ["docker-metadata-action"]
  context = "."
  dockerfile = "Dockerfile"
  // Platform will be set from GitHub Actions
  // cache-from and cache-to will also be set from GitHub Actions
  args = {
    PYTHON_VERSION = "3.12.8"
    // Additional build args can be defined here
  }
  // Output image will be pushed if push=true is set in GitHub Actions
}

// Group target to build both platforms
group "default" {
  targets = ["build"]
}

// Optional specific targets for each platform if needed
target "amd64" {
  inherits = ["build"]
  platforms = ["linux/amd64"]
  cache-from = ["type=gha,scope=linux/amd64"]
  cache-to = ["type=gha,mode=max,scope=linux/amd64"]
}

target "arm64" {
  inherits = ["build"]
  platforms = ["linux/arm64"]
  cache-from = ["type=gha,scope=linux/arm64"]
  cache-to = ["type=gha,mode=max,scope=linux/arm64"]
  // Optional arm64-specific args
  args = {
    PYTHON_VERSION = "3.12.8"
    OPENBLAS_NUM_THREADS = "1"
    MKL_NUM_THREADS = "1"
    NUMEXPR_NUM_THREADS = "1"
  }
}

// Matrix build target if you prefer to use it directly in bake
target "multi-platform" {
  inherits = ["build"]
  platforms = ["linux/amd64", "linux/arm64"]
}
