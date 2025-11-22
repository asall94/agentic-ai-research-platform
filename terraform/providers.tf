terraform {
  required_version = ">= 1.0"
  
  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.0"
    }
  }
}

provider "render" {
  # API key from environment variable RENDER_API_KEY
  # or set via: export RENDER_API_KEY=your_key
}
