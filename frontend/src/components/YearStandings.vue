<template>
  <q-card flat bordered>
    <q-card-section class="q-pb-sm">
      <div class="text-subtitle1">Yearly standings matrix</div>
      <div class="text-caption text-grey-7">
        Dummy view – Need to think about a good display and more data required
      </div>
    </q-card-section>

    <q-separator />

    <q-card-section class="q-pa-none">
      <q-markup-table flat dense class="q-pa-sm">
        <thead>
        <tr>
          <th class="text-left">Player</th>
          <th class="text-center">1st place</th>
          <th class="text-center">2nd place</th>
          <th class="text-center">3rd place</th>
          <th class="text-center">4th place</th>
        </tr>
        </thead>
        <tbody>
        <!-- Dummy rows – adjust counts however you like -->
        <tr>
          <td class="text-left text-weight-medium">MissM1</td>
          <td class="text-center"><q-badge color="primary"  rounded>3</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>0</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>0</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">Ginooo</td>
          <td class="text-center"><q-badge color="primary"  rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>0</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">haligh</td>
          <td class="text-center"><q-badge color="primary"  rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>1</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">isiundossi</td>
          <td class="text-center"><q-badge color="primary"  rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>3</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>2</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">Palladium2000</td>
          <td class="text-center"><q-badge color="primary"  rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>0</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">Bienchen2000</td>
          <td class="text-center"><q-badge color="primary"  rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>1</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">eumel247</td>
          <td class="text-center"><q-badge color="primary"  rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>1</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">Feuterim</td>
          <td class="text-center"><q-badge color="primary"  rounded>0</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>3</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>1</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">Zimbaland</td>
          <td class="text-center"><q-badge color="primary"  rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>0</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>3</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">Bob</td>
          <td class="text-center"><q-badge color="primary"  rounded>0</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>4</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">MobMob3</td>
          <td class="text-center"><q-badge color="primary"  rounded>0</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>1</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>3</q-badge></td>
        </tr>
        <tr>
          <td class="text-left text-weight-medium">chefkoch07</td>
          <td class="text-center"><q-badge color="primary"  rounded>0</q-badge></td>
          <td class="text-center"><q-badge color="secondary" rounded>0</q-badge></td>
          <td class="text-center"><q-badge color="orange"   rounded>2</q-badge></td>
          <td class="text-center"><q-badge color="grey-5"   rounded>4</q-badge></td>
        </tr>
        </tbody>
      </q-markup-table>
    </q-card-section>
  </q-card>
</template>
