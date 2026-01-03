FROM busybox:latest

# Copy all bundled flows from source
COPY ../flows/ /bundled-flows/

# Set permissions
RUN chmod -R 755 /bundled-flows

CMD ["cp", "-r", "/bundled-flows/", "/workspace/"]
