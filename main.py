
import asyncio
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class CalculateRequest(BaseModel):
    numbers: list[int]
    delays: list[float] = Field(min_length=1)


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

    if any(delay < 0 for delay in data.delays):
        raise HTTPException(
            status_code=400,
            detail="Задержка не может быть отрицательной",
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
