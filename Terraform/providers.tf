terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "github" {
  owner = "norahosny66"
  token = "GITHUB_TOKEN" # or `GITHUB_TOKEN`
}