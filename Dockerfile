
FROM python:3.9.17-bookworm AS builder
# base for compile python scripts to binary
RUN ln -s /lib/aarch64-linux-gnu/libnss_dns.so.2 /lib/aarch64-linux-gnu/libnss_dns.so
RUN ln -s /lib/aarch64-linux-gnu/libnss_files.so.2 /lib/aarch64-linux-gnu/libnss_files.so
RUN pip install SCons==4.5.2 patchelf==0.16.1  # must be installed before staticx
RUN pip install pyinstaller==5.12.0  staticx==0.13.9

# the project requirements
ADD requirements.txt /app/requirements.txt 
WORKDIR /app
RUN pip install -r requirements.txt 
COPY . /app

# compile the python scripts to single binary
RUN pyinstaller -F run_backup.py &&  staticx ./dist/run_backup ./static 


# store binary in another image with only the binary
FROM scratch
COPY --from=builder /app/static /run_backup/
COPY --from=builder /tmp /tmp
WORKDIR /run_backup
ENTRYPOINT ["./static"]


