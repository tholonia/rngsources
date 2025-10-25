import { Client, DIRNGClient } from '@buff-beacon-project/curby-client';

async function main() {
  const client = Client.create();
  const randomness = await client.randomness();

  const myArray = [1, 2, 3, 4, 5];
  const shuffled = randomness.shuffled(myArray);
  console.log('Shuffled array:', shuffled);

  const dirng = DIRNGClient.create();
  const latest = await dirng.latest();
  console.log(`Got info for round ${latest.round}. Stage is ${latest.stage}`);
}

main().catch(console.error);
