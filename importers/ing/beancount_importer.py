"""Example importer for example broker UTrade.
"""

__copyright__ = "Copyright (C) 2016  Martin Blais"
__license__ = "GNU GPLv2"

import re
from os import path

import pandas as pd
from beancount.core import amount, data
from beancount.core.number import D
from beancount.ingest import importer

categories = {
    "Hogar": {
        "translation": "Home",
        "account_type": "Expenses",
        "subcategories": {
            "Agua": "Water",
            "Alquiler trastero y garaje": "StorageGarageRent",
            "Alquiler vivienda": "Rent",
            "Comunidad": "Community",
            "Decoración y mobiliario": "DecorationFurniture",
            "Hipoteca": "Mortgage",
            "Hogar (otros)": "HomeOther",
            "Impuestos hogar": "HomeTaxes",
            "Limpieza": "Cleaning",
            "Luz y gas": "ElectricityGas",
            "Mantenimiento del hogar": "HomeMaintenance",
            "Seguridad y alarmas": "SecurityAlarms",
            "Seguro de hogar": "HomeInsurance",
            "Teléfono, TV e internet": "PhoneTVInternet",
        },
    },
    "Vehículo y transporte": {
        "translation": "VehicleTransport",
        "account_type": "Expenses",
        "subcategories": {
            "Gasolina y combustible": "GasolineFuel",
            "Impuestos del vehículo": "VehicleTaxes",
            "Mantenimiento de vehículo": "VehicleMaintenance",
            "Multas": "Fines",
            "Parking y garaje": "ParkingGarage",
            "Peajes": "Tolls",
            "Préstamo de vehículo": "VehicleLoan",
            "Recarga vehículo eléctrico": "ElectricVehicleRecharge",
            "Seguro de coche y moto": "CarMotorcycleInsurance",
            "Taxi y Carsharing": "TaxiCarsharing",
            "Transporte público": "PublicTransport",
            "Vehículo y transporte (otros)": "VehicleTransportOther",
        },
    },
    "Compras": {
        "translation": "Shopping",
        "account_type": "Expenses",
        "subcategories": {
            "Belleza, peluquería y perfumería": "BeautyHairdressingPerfumery",
            "Compras (otros)": "ShoppingOther",
            "Electrónica": "Electronics",
            "Mascotas y veterinario": "PetsVeterinary",
            "Regalos y juguetes": "GiftsToys",
            "Ropa y complementos": "ClothingAccessories",
            "Tarjetas financieras y de crédito": "FinancialCreditCards",
        },
    },
    "Ocio y viajes": {
        "translation": "LeisureTravel",
        "account_type": "Expenses",
        "subcategories": {
            "Alquiler vehículo": "VehicleRental",
            "Billetes de viaje": "TravelTickets",
            "Cafeterías y restaurantes": "CafesRestaurants",
            "Cine, teatro y espectáculos": "CinemaTheatreShows",
            "Estancos y tabaco": "Tobacco",
            "Gastos desplazamiento": "TravelExpenses",
            "Hotel y alojamiento": "HotelAccommodation",
            "Libros, música y videojuegos": "BooksMusicVideoGames",
            "Loterías y apuestas": "LotteriesBets",
            "Ocio y viajes (otros)": "LeisureTravelOther",
            "Seguro de viaje": "TravelInsurance",
        },
    },
    "Otros gastos": {
        "translation": "OtherExpenses",
        "account_type": "Expenses",
        "subcategories": {
            "Asociaciones y colegios profesionales": "AssociationsProfessionalColleges",
            "Autónomos": "Freelancers",
            "Cajeros": "ATMs",
            "Cheques": "Checks",
            "Comisiones e intereses": "CommissionsInterests",
            "Gasto Bizum": "BizumExpense",
            "ONG": "NGO",
            "Otros gastos (otros)": "OtherExpensesOther",
            "Otros préstamos y avales": "OtherLoansGuarantees",
            "Otros seguros": "OtherInsurances",
            "Pagos impuestos": "TaxPayments",
            "Pensión alimenticia": "Alimony",
            "Sindicatos": "Unions",
            "Suscripciones": "Subscriptions",
            "Transferencias": "Transfers",
        },
    },
    "Alimentación": {
        "translation": "Food",
        "account_type": "Expenses",
        "subcategories": {
            "Alimentación (otros)": "FoodOther",
            "Bodega y Gourmet": "WineryGourmet",
            "Comida a domicilio": "HomeDelivery",
            "Supermercados y alimentación": "SupermarketsFood",
        },
    },
    "Educación, salud y deporte": {
        "translation": "EducationHealthSport",
        "account_type": "Expenses",
        "subcategories": {
            "Actividades extraescolares": "ExtracurricularActivities",
            "Dentista, médico": "DentistDoctor",
            "Deporte y gimnasio": "SportGym",
            "Educación": "Education",
            "Educación, salud y deporte (otros)": "EducationHealthSportOther",
            "Farmacia, herbolario y nutrición": "PharmacyHerbalistNutrition",
            "Guardería y cuidado de niños": "NurseryChildcare",
            "Óptica": "Optics",
            "Seguro de salud": "HealthInsurance",
            "Seguro de vida": "LifeInsurance",
        },
    },
    "Nómina y otras prestaciones": {
        "translation": "PayrollAndOtherBenefits",
        "account_type": "Income",
        "subcategories": {
            "Nómina o Pensión": "PayrollPension",
            "Otros nómina y prestaciones": "OtherPayrollBenefits",
            "Pensión alimenticia": "Alimony",
            "Prestación por desempleo": "UnemploymentBenefits",
        },
    },
    "Otros ingresos": {
        "translation": "OtherIncome",
        "account_type": "Income",
        "subcategories": {
            "Abono de financiación": "FundingPayment",
            "Ingreso Bizum": "BizumIncome",
            "Ingresos de cheques": "CheckIncome",
            "Ingresos de efectivo": "CashIncome",
            "Ingresos de impuestos": "TaxIncome",
            "Ingresos de otras entidades": "IncomeOtherEntities",
            "Ingresos por alquiler": "RentalIncome",
            "Otros ingresos (otros)": "OtherIncomeOther",
        },
    },
    "Inversión": {
        "translation": "Investment",
        "account_type": "Assets",
        "subcategories": {
            "Acciones": "Shares",
            "Fondos de inversión": "InvestmentFunds",
            "Otras inversiones": "OtherInvestments",
            "Planes de pensiones": "PensionPlans",
        },
    },
    "Ahorro": {
        "translation": "Savings",
        "account_type": "Assets:EU:ING",
        "subcategories": {
            "Otros ahorros": "OtherSavings",
            "Productos de ahorro": "SavingsProducts",
            "Redondeo": "Rounding",
        },
    },
    "Movimientos excluidos": {
        "translation": "ExcludedMovements",
        "account_type": "Expenses",
        "subcategories": {
            "Transacción entre cuentas de ahorro": "TransactionBetweenSavingsAccounts",
            "Traspaso entre cuentas": "TransferBetweenAccounts",
        },
    },
    "Ventajas ING": {
        "translation": "INGAdvantages",
        "account_type": "Income",
        "subcategories": {
            "Abono de intereses": "InterestPayment",
            "Abono de promociones": "PromotionPayment",
            "Otras Ventajas ING": "OtherINGAdvantages",
        },
    },
}


class Importer(importer.ImporterProtocol):
    """An importer for UTrade CSV files (an example investment bank)."""

    def __init__(
        self,
        currency,
        account_root,
        folder,
        # account_cash,
        # account_dividends,
        # account_gains,
        # account_fees,
        account_external,
    ):
        self.currency = currency
        self.account_root = account_root
        self.folder = folder

        if self.folder == "credit":
            self.worksheet = "Tarjetas"
            self.date_column = "FECHA VALOR"
            self.description_column = "DESCRIPCION"
            self.header = 6
        else:
            self.worksheet = "Movimientos"
            self.date_column = "F. VALOR"
            self.description_column = "DESCRIPCIÓN"
            self.header = 5
        # self.account_cash = account_cash
        # self.account_dividends = account_dividends
        # self.account_gains = account_gains
        # self.account_fees = account_fees
        self.account_external = account_external

    def identify(self, file):
        # Match if the filename is as downloaded and the header has the unique
        # fields combination we're looking for.
        """
        from beancount.ingest import cache
        file = cache.get_file("/home/pmercatoris/MyDrive/finance/documents/ing/in/checking/2024/march.xls")
        file = cache.get_file("/home/pmercatoris/MyDrive/finance/documents/ing/xls/credit/2024/january.xls")
        folder = 'credit'
        """

        match = re.match(r".+\.xls", path.basename(file.name)) and (
            f"/{self.folder}/" in path.dirname(file.name)
        )
        return match

    def file_name(self, file):
        return "ing.{}".format(path.basename(file.name))

    def file_account(self, _):
        return self.account_root

    def read_df(self, file):
        # Open the CSV file and create directives.
        """
        df = pd.read_excel(file.name, sheet_name="Tarjetas", header=5, dtype=str)
        """
        df = pd.read_excel(
            file.name, sheet_name=self.worksheet, header=self.header, dtype=str
        )
        df[self.date_column] = pd.to_datetime(df[self.date_column]).dt.date
        return df

    def file_date(self, file):
        # Extract the statement date from the filename.
        # read the file and extract the date from the first row
        df = self.read_df(file)
        my_file_date = df[self.date_column].iloc[0]
        return my_file_date

    def extract(self, file):
        # Open the CSV file and create directives.
        transactions = []
        index = 0
        df = self.read_df(file)

        for index, row in df.iterrows():
            # if float(row["IMPORTE (€)"])<-30000:
            #     break
            meta = data.new_metadata(file.name, index)
            date = row[self.date_column]
            description = row[self.description_column]

            # Assign accounts based on category and subcategory
            categoria = row["CATEGORÍA"] if pd.notna(row["CATEGORÍA"]) else "Unknown"
            subcategoria = (
                row["SUBCATEGORÍA"] if pd.notna(row["SUBCATEGORÍA"]) else "Unknown"
            )

            category = categories.get(
                categoria, dict(translation=categoria, subcategories=dict())
            )
            subcategory = category["subcategories"].get(subcategoria, subcategoria)

            if category["translation"] == "Movimiento sin categoría":
                if subcategory == "Transacción entre cuentas de ahorro":
                    account = "Assets:EU:ING:Savings:TransferBetweenAccounts"

            else:
                account_type = category.get(
                    "account_type",
                    "Expenses" if float(row["IMPORTE (€)"]) < 0 else "Income",
                )

                account = "{account_type}:{category}:{subcategory}".format(
                    account_type=account_type,
                    category=category["translation"],
                    subcategory=subcategory,
                )

            # Create the Posting object
            postings = []
            postings.append(
                data.Posting(
                    self.account_external,
                    amount.Amount(D(row["IMPORTE (€)"]), self.currency),
                    None,
                    None,
                    None,
                    None,
                )
            )
            postings.append(
                data.Posting(
                    account,
                    amount.Amount(-D(row["IMPORTE (€)"]), self.currency),
                    None,
                    None,
                    None,
                    None,
                )
            )

            # Create the Transaction object
            transaction = data.Transaction(
                meta=meta,
                date=date,
                payee=None,
                flag="*",
                narration=description,
                tags=set(),
                links=set(),
                postings=postings,
            )

            transactions.append(transaction)

        # Insert a final balance check.
        # if index:
        #     entries.append(
        #         data.Balance(
        #             meta,
        #             date + datetime.timedelta(days=1),
        #             self.account_cash,
        #             amount.Amount(D(row["BALANCE"]), self.currency),
        #             None,
        #             None,
        #         )
        #     )

        return transactions
