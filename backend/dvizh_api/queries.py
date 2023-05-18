from string import Template

loanOfficer_SignIn = Template(
    """
    mutation loanOfficer_SignIn {
        loanOfficer_SignIn (input: {
            email: "$email",
            password: "$password"
        })
    }
    """
)

getLoanOffer = Template(
    """
    query {
        getLoanOffer(
            loanPeriod: 10,
            initialPaymentPercent: 20,
            agendaType: $agenda_type,
            housingComplexId: $complex_id,
            mortgageType: $mortgage_type,
            isRfCitizen: true,
            cost: $cost,
            strictlyMatchesLoanPeriod: false,
            employmentType: employee,
            lastJobExp: 100,
            overallExp: 100,
            age: 35
        ){
            id,
            bankId,
            maxCreditAmount,
            maxCreditPeriod,
            minInitialPayment,
            name,
            rate
        }
    }
    """
)

getHousingComplexBankByHousingComplexUuid = Template(
    """
    query {
        getHousingComplexBankByHousingComplexUuid(
            uuid:"$uuid"
        ){
            collection {
                uuid
                bank {
                    externalId,
                    logo,
                    name
                }
            }
        }
    }
    """
)

getHousingComplex = Template(
    """
    query {
        getHousingComplex {
            collection {
                isActive,
                externalId,
                name,
                uuid
            }
        }
    }
    """
)
