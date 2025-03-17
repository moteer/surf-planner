
@app.get("/surfplan/{date}", response_model=SurfPlanResponse)
def get_surfplan(date: str):
    # Query tide data for the specific date
    # tides = db.query(Tide).filter(Tide.timestamp.between(f"{date} 00:00:00", f"{date} 23:59:59")).order_by(Tide.timestamp).all()
    tides = get_tides(date)

    return TidesResponse(
        date=date,
        tides=[TideResponse(timestamp=tide.timestamp, height=tide.height, type=tide.type) for tide in tides]
    )


# Run the API with Uvicorn
if __name__ == "__main__":
    pass
