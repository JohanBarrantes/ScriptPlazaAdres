from copy import deepcopy
from pickle import TRUE  # noqa: F401
import jinja2

from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from constants import EmptyStringDiff, loggerConfig
from barcode import Gs1_128  # noqa: F401
from barcode.writer import ImageWriter  # noqa: F401
import treepoem
from jsonpath_ng import jsonpath, parse  # noqa: F401

import logging

logging.basicConfig(format=loggerConfig)


class TemplateManager:
    def __init__(
        self, templateFilePath=EmptyStringDiff, barcodesFolder=EmptyStringDiff
    ):
        self.templateFilePath = templateFilePath
        self.barcodesFolder = barcodesFolder
        self.jinjaEnviorement = None
        self.barcodesPaths = []
        self.setupJinjaEnvironment()

    def setupJinjaEnvironment(self):
        self.jinjaEnviorement = jinja2.Environment()
        self.jinjaEnviorement.filters[
            "col_number_format"
        ] = TemplateManager.col_number_format
        self.jinjaEnviorement.add_extension("jinja2.ext.do")

    def generateDocument(self, context={}, destinationFilepath=EmptyStringDiff):
        template = DocxTemplate(self.templateFilePath)
        content = deepcopy(context)

        self.generateBarcodes(content, template)

        self.addKeyWords(content)

        template.render(content, self.jinjaEnviorement)
        template.save(destinationFilepath)

    def generateBarcodes(self, context, template):
        # Using jsonpath to find the value of the bar_code_text key in the context dictionary.
        jsonpath_expr = parse("$..bar_code_text")
        match = jsonpath_expr.find(context)
        if match:
            barcodeInput = match[0].value
            barcodePath = f"{self.barcodesFolder}{barcodeInput}.jpg"
            # Generating the barcode.
            image = treepoem.generate_barcode(
                barcode_type="gs1-128",  # One of the BWIPP supported codes.
                data=barcodeInput,
                options={
                    "includetext": False,
                },
            )
            image.convert("1").save(barcodePath)

            widthBarcode = self.widthBarcode(barcodeInput)

            jsonpath_expr = parse("$..barcode")
            # Adding the barcode to the template.
            jsonpath_expr.update(
                context,
                InlineImage(
                    template, barcodePath, width=Mm(widthBarcode), height=Mm(20.00)
                ),
            )

            self.barcodesPaths.append(barcodePath)

    def addKeyWords(self, context):
        context["page_break"] = "\f"

    def getBarcodesPaths(self):
        return self.barcodesPaths

    def widthBarcode(self, barcodeText):
        """
        Return the width of the barcode.
        M=11    CONSTANT Modules
        C=66    CONSTANT
        R=0.25  The percentage of reduction
        S=3     number Of separators
        N:      (The number of characters barcode / 2) + number Of separators
        width = ( (M * N) + C) x R

        Example with barcode:
        - (415)7709998416949(8020)990194900000084732(3900)0000001000(96)20221031
        Replace "(" and  ")" for "":
        - 41577099984169498020990194900000084732390000000010009620221031
        Length of the barcode:
        - 62 = len(41577099984169498020990194900000084732390000000010009620221031)
        Dividing the length of the barcode by 2 and add number Of separators.
        - N = (len/2) + S
        - N = (62/2) + 3
        - N = 34
        Apply formula
        - width = ( (M * N) + C) x R
        - width = ( (11 * 34) + 66) * 0.25
        - width = 110.0

        :param barcodeText: The barcode text
        :return: The width of the barcode.
        """
        constNumber = 66  # C constant
        modules = 11  # M modules
        rate = 0.25  # R The percentage of reduction.
        numberOfSeparators = 3  # S number Of separators
        barcodeText = barcodeText.replace("(", "").replace(
            ")", ""
        )  # Removing the parenthesis from the barcode text.
        totalPairs = (
            len(barcodeText) / 2
        ) + numberOfSeparators  # Calculating the number of pairs of characters in the barcode.

        return ((modules * totalPairs) + constNumber) * rate

    @staticmethod
    def col_number_format(value, decimal_number=2):
        default_value = 0
        str_format = "{:_." + str(decimal_number) + "f}"
        if value:
            return str_format.format(float(value)).replace(".", ",").replace("_", ".")
        else:
            return (
                str_format.format(float(default_value))
                .replace(".", ",")
                .replace("_", ".")
            )
