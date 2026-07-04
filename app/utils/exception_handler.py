import sys
import logging
from PySide6.QtWidgets import QMessageBox, QApplication
from sqlalchemy.orm import Session
from app.models.models import LogSistema

# Configuração básica de log no console para desenvolvimento
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class GlobalExceptionHandler:
    def __init__(self, db_session: Session):
        self.db = db_session

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Captura qualquer erro não tratado na aplicação Qt, loga no banco e avisa o usuário."""
        # Ignora o fechamento normal do teclado (Ctrl+C)
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        mensagem_erro = f"{exc_type.__name__}: {exc_value}"
        import traceback
        trace_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # 1. Exibe no console do desenvolvedor
        logging.error(f"Exceção não capturada: {mensagem_erro}\n{trace_str}")

        # 2. Grava o log de erro no banco de dados para auditoria militar
        try:
            log_banco = LogSistema(
                nivel="ERROR",
                mensagem=mensagem_erro,
                exception=trace_str,
                usuario_id=None # Pode ser expandido se houver sessão global do operador
            )
            self.db.add(log_banco)
            self.db.commit()
        except Exception as db_err:
            logging.error(f"Falha crítica ao salvar log no banco: {db_err}")

        # 3. Exibe uma mensagem amigável para o operador na guarita (evita crash do app)
        # Garante que a caixa de mensagem abra na thread principal do Qt
        if QApplication.instance():
            QMessageBox.critical(
                None,
                "Erro Interno do Sistema",
                f"Ocorreu uma falha inesperada no SisCAM.\n\nDetalhes: {exc_value}\n\nO incidente foi registrado para a equipe de TI."
            )