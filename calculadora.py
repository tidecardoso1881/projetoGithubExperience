"""Calculadora com operações e memória de cálculo.

Contém as classes `Memory` e `Calculator`. A `Calculator` oferece operações
básicas e algumas avançadas, além de registrar cada cálculo na memória.

Uso rápido (linha de comando):
  python calculadora.py
"""
from __future__ import annotations
import math
import ast
import operator as op
from typing import Any, List, Optional, Dict


class Memory:
	"""Armazena histórico de cálculos.

	Histórico é uma lista de dicionários: {'expr': str, 'result': Any}
	"""

	def __init__(self) -> None:
		self._history: List[Dict[str, Any]] = []

	def store(self, expr: str, result: Any) -> None:
		self._history.append({'expr': expr, 'result': result})

	def recall_all(self) -> List[Dict[str, Any]]:
		return list(self._history)

	def recall(self, index: int) -> Dict[str, Any]:
		return self._history[index]

	def clear(self) -> None:
		self._history.clear()

	def __len__(self) -> int:
		return len(self._history)


class Calculator:
	"""Calculadora que registra operações na `Memory`.

	Exemplo de uso:
		calc = Calculator()
		calc.add(2,3)  # 5, registrado na memória
	"""

	def __init__(self, memory: Optional[Memory] = None) -> None:
		self.memory = memory or Memory()
		self.last: Optional[Any] = None

	def _record(self, expr: str, result: Any) -> Any:
		self.last = result
		try:
			self.memory.store(expr, result)
		except Exception:
			pass
		return result

	def add(self, a: float, b: float) -> float:
		return self._record(f"{a} + {b}", a + b)

	def sub(self, a: float, b: float) -> float:
		return self._record(f"{a} - {b}", a - b)

	def mul(self, a: float, b: float) -> float:
		return self._record(f"{a} * {b}", a * b)

	def div(self, a: float, b: float) -> float:
		if b == 0:
			raise ZeroDivisionError("Divisão por zero")
		return self._record(f"{a} / {b}", a / b)

	def pow(self, a: float, b: float) -> float:
		return self._record(f"{a} ** {b}", a ** b)

	def sqrt(self, a: float) -> float:
		if a < 0:
			raise ValueError("Raiz quadrada de número negativo")
		return self._record(f"sqrt({a})", math.sqrt(a))

	def percent(self, value: float, percent: float) -> float:
		"""Retorna 'percent' por cento de 'value'."""
		return self._record(f"{percent}% de {value}", value * percent / 100.0)

	def negate(self, a: float) -> float:
		return self._record(f"neg({a})", -a)

	def reciprocal(self, a: float) -> float:
		if a == 0:
			raise ZeroDivisionError("Recíproco de zero")
		return self._record(f"1/{a}", 1.0 / a)

	# --- avaliação segura de expressões ---
	_operators = {
		ast.Add: op.add,
		ast.Sub: op.sub,
		ast.Mult: op.mul,
		ast.Div: op.truediv,
		ast.Pow: op.pow,
		ast.Mod: op.mod,
		ast.USub: op.neg,
		ast.UAdd: op.pos,
	}

	def _eval_ast(self, node: ast.AST) -> float:
		if isinstance(node, ast.Num):  # type: ignore[attr-defined]
			return node.n  # type: ignore[attr-defined]
		if isinstance(node, ast.Constant):
			if isinstance(node.value, (int, float)):
				return node.value
			raise ValueError("Constante não-numérica na expressão")
		if isinstance(node, ast.BinOp):
			left = self._eval_ast(node.left)
			right = self._eval_ast(node.right)
			op_func = self._operators.get(type(node.op))
			if op_func is None:
				raise ValueError("Operador não suportado")
			return op_func(left, right)
		if isinstance(node, ast.UnaryOp):
			operand = self._eval_ast(node.operand)
			op_func = self._operators.get(type(node.op))
			if op_func is None:
				raise ValueError("Operador unário não suportado")
			return op_func(operand)
		if isinstance(node, ast.Expr):
			return self._eval_ast(node.value)
		raise ValueError("Nó AST não suportado")

	def evaluate(self, expression: str) -> float:
		"""Avalia uma expressão numérica de forma segura e registra o resultado.

		Suporta +, -, *, /, **, %, parênteses e números.
		"""
		try:
			parsed = ast.parse(expression, mode='eval')
			result = self._eval_ast(parsed.body)  # type: ignore[attr-defined]
		except Exception as exc:
			raise ValueError(f"Expressão inválida: {exc}")
		return self._record(expression, result)


def _demo() -> None:
	calc = Calculator()
	print("Calculadora interativa. Digite 'help' para comandos.")
	while True:
		try:
			s = input('> ').strip()
		except (EOFError, KeyboardInterrupt):
			print('\nSaindo...')
			break
		if not s:
			continue
		if s.lower() in {'q', 'quit', 'exit'}:
			print('Saindo...')
			break
		if s.lower() in {'h', 'help'}:
			print('Comandos: help, history, memclear, last, quit')
			print('Também é possível digitar uma expressão, ex: 2+3*4')
			continue
		if s.lower() == 'history':
			for i, item in enumerate(calc.memory.recall_all()):
				print(f"{i}: {item['expr']} = {item['result']}")
			continue
		if s.lower() == 'memclear':
			calc.memory.clear()
			print('Memória limpa')
			continue
		if s.lower() == 'last':
			print(calc.last)
			continue
		# tentar avaliar como expressão
		try:
			res = calc.evaluate(s)
			print(res)
		except Exception:
			print('Comando ou expressão inválida. Digite help.')


if __name__ == '__main__':
	_demo()

