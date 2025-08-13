FROM jenkins/jenkins:lts

USER root

# Match host docker group GID
RUN groupadd -g 999 docker \
  && usermod -aG docker jenkins

# Optional: install Docker CLI
RUN apt-get update && apt-get install -y docker.io

USER jenkins
