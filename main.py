
import asyncio
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI()


class CalculateRequest(BaseModel):
    numbers: list[int] = Field(min_length=1, max_length=100)
    delays: list[float] = Field(min_length=1, max_length=100)

    @field_validator("delays")
    @classmethod
    def validate_delays(cls, delays: list[float]) -> list[float]:
        if any(delay < 0 or delay > 10 for delay in delays):
            raise ValueError("Задержка должна быть от 0 до 10 секунд")

        return delays


class CalculateResult(BaseModel):
    number: int
    square: int
    delay: float
    time: float


class CalculateResponse(BaseModel):
    results: list[CalculateResult]
    total_time: float
    parallel_faster_than_sequential: bool


async def calculate_square(number: int, delay: float) -> CalculateResult:
    start = time.perf_counter()

    await asyncio.sleep(delay)

    return CalculateResult(
        number=number,
        square=number ** 2,
        delay=delay,
        time=round(time.perf_counter() - start, 2),
    )


@app.post("/calculate/")
async def calculate(data: CalculateRequest) -> CalculateResponse:
    if len(data.numbers) != len(data.delays):
        raise HTTPException(
            status_code=400,
            detail="Количество чисел и задержек должно совпадать",
        )

    start = time.perf_counter()

    tasks = [
        calculate_square(number, delay)
        for number, delay in zip(data.numbers, data.delays)
    ]

    results = await asyncio.gather(*tasks)
    total_time = round(time.perf_counter() - start, 2)

    return CalculateResponse(
        results=results,
        total_time=total_time,
        parallel_faster_than_sequential=total_time < sum(data.delays),
    )