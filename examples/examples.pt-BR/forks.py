from socketify import App
import os
import multiprocessing

def run_app():
    app = App()
    app.get("/", lambda res, req: res.end("Hello, World!"))
    app.listen(
        3000,
        lambda config: print(
            "PID %d Listening on port http://localhost:%d now\n"
            % (os.getpid(), config.port)
        ),
    )
    app.run()


pid_list = []
# Bifurca limitando a contagem de CPU - 1
for _ in range(1, multiprocessing.cpu_count()):
    pid = os.fork()
    # número maior que 0 significa processamento familiar
    if not pid > 0:
        run_app()
        break
    pid_list.append(pid)

run_app()  # Excuta esse app no processo principal também :)

# Ativar tudo para o desligamento normal 
import signal
for pid in pid_list:
    os.kill(pid, signal.SIGINT)