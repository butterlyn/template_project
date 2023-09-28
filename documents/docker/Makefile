# Set sensitive information from user as environment variables
echo "Enter OpenAI key (or leave blank): "
read OPENAI_KEY

DATE_KEY=$(date +%y-%m-%d_%H:%M)
echo 'Setting dev_container image tag to datetime key: '
echo "$DATETIME_KEY"

# build dev container
sudo docker buildx build —-tag dev_container:"$DATETIME_KEY" --file ./dev_container.dockerfile --pull --build-arg OPENAI_KEY="$OPENAI_KEY"

# run dev container
sudo docker run dev_container:"$DATETIME_KEY" -it --name dev_container --volume "$HOME"/Documents:/root/documents/mount --volume "$HOME"/.ssh:/root/.ssh