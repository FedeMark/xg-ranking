import pandas as pd
from ranking import Ranking


def main(MATCH_DAY=26):
    df = pd.read_html(
        "https://fbref.com/it/comp/11/calendario/Risultati-e-partite-di-Serie-A"
    )
    df = df[0]

    df.rename(columns={"xG": "xG_home", "xG.1": "xG_away"}, inplace=True)
    df.drop(
        columns=["Giorno", "Stadio", "Arbitro", "Report partita", "Note", "Spettatori"],
        inplace=True,
    )
    df.sort_values(by=["Data", "Ora"], ascending=True, inplace=True)

    to_pred = df[df["Sett."] == MATCH_DAY]

    df.dropna(inplace=True)
    teams = df.Casa.unique()
    teams.sort()

    ranking = Ranking(teams=teams, gamma=0.15, starting_xG=1, starting_xGA=1)
    tables = []
    match_day = MATCH_DAY

    for m in range(1, match_day):
        m_df = df[df["Sett."] == m]
        for i, row in m_df.iterrows():
            ranking.update_after_match(
                home=row["Casa"],
                away=row["Ospiti"],
                xG_home=row["xG_home"],
                xG_away=row["xG_away"],
            )
        table = ranking.table
        table["Game"] = m
        tables.append(table)

    table = pd.concat(tables)

    for _, row in to_pred.iterrows():
        print(
            row["Casa"],
            row["Ospiti"],
            ranking.predict_match(home=row["Casa"], away=row["Ospiti"]),
        )


if __name__ == "__main__":
    main()
