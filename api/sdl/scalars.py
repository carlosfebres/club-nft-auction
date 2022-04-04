from typing import Optional, Union

from tartiflette import Scalar

# todo: implement
@Scalar("Color")
class Color:
    @staticmethod
    def coerce_input(val):
        return val

    @staticmethod
    def coerce_output(val):
        return val

    def parse_literal(self, ast: "valueNode") -> Union[str, "UNDEFINED_VALUE"]:
        if isinstance(ast, StringValueNode):
            return ast.value
        return UNDEFINED_VALUE

@Scalar("Timestamp")
class Timestamp:
    @staticmethod
    def coerce_input(val):
        return val

    @staticmethod
    def coerce_output(val):
        return val

    def parse_literal(self, ast: "valueNode") -> Union[str, "UNDEFINED_VALUE"]:
        if isinstance(ast, StringValueNode):
            return ast.value
        return UNDEFINED_VALUE

@Scalar("KongImage")
class KongImage:
    @staticmethod
    def coerce_input(val):
        return val

    @staticmethod
    def coerce_output(val):
        return val

    def parse_literal(self, ast: "valueNode") -> Union[str, "UNDEFINED_VALUE"]:
        if isinstance(ast, StringValueNode):
            return ast.value
        return UNDEFINED_VALUE

@Scalar("LogoImage")
class LogoImage:
    @staticmethod
    def coerce_input(val):
        return val

    @staticmethod
    def coerce_output(val):
        return val

    def parse_literal(self, ast: "valueNode") -> Union[str, "UNDEFINED_VALUE"]:
        if isinstance(ast, StringValueNode):
            return ast.value
        return UNDEFINED_VALUE
