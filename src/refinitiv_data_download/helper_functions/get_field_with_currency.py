
def to_target_currency(field: str, currency: str):

    """This defines a list of fields that do not have a currency component
    Any field not in the list will be modified to include the currency component."""

    no_curn = {
        "TR.GICSSector",
        "TR.GICSIndustryGroup",
        "TR.GICSIndustry",
        "TR.TRBCEIndustry",
        "TR.TRBCEIndustryGroup",
        "TR.ICBSector",
        "TR.ICBIndustry",
        "TR.PriceClose.Currency",
        "TR.ExchangeCountry",
        "TR.ExchangeMarketIdCode",
        "TR.TRESGScore",
        "TR.PriceToBVPerShare",
        "TR.IndexConstituentRIC",
        "TR.IndexConstituentShares",
        "TR.IndexDivisor",
        "TR.SharesOutstanding",
        "TR.DivExDate",
        "TR.DivExDate.periodenddate",
        "TR.DivType",
        "TR.DivPaymentType",
        "TR.DivCurr",
        "TR.DivIsRescinded",
        "TR.DivRescindDate",
        "TR.DivAdjustedGross.periodenddate",
        "TR.OperatingIncome.periodenddate",
        "TR.TotalEquity.periodenddate", 
        "TR.TotalAssets.periodenddate",
        "TR.TotalAssetsReported.periodenddate",
        "TR.OperatingIncome",
        "TR.TotalEquity",
        "TR.TotalAssetsReported",
        "TR.TotalAssets",
        "TR.ISOriginalAnnouncementDate",
        "TR.CoRPrimaryCountry",
        "TR.HeadquartersCountry",    
        "TR.EntryDate",
        "TR.EffectiveFromDate",
        "TR.EffectiveToDate",
    }

    if field in no_curn:
        return field
    
    if "(" in field and field.endswith(")"):
        return field[:-1] + f",Curn={currency})"
    else:
        return f"{field}(Curn={currency})"

